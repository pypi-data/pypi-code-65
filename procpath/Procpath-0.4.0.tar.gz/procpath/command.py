import asyncio.subprocess
import contextlib
import itertools
import json
import logging
import os
import signal
import string
import time
from datetime import datetime

import jsonpyth

from . import proctree, procfile, procrec, procret, utility


__all__ = 'CommandError', 'query', 'record', 'plot', 'watch'

logger = logging.getLogger(__package__)


class CommandError(Exception):
    """Generic command error."""


def query(procfile_list, output_file, delimiter=None, indent=None, query=None):
    readers = {k: v for k, v in procfile.registry.items() if k in procfile_list}
    tree = proctree.Tree(readers)
    result = tree.get_root()

    if query:
        try:
            result = jsonpyth.jsonpath(result, query, always_return_list=True)
        except jsonpyth.JsonPathSyntaxError as ex:
            raise CommandError(str(ex)) from ex

    if delimiter:
        result = delimiter.join(map(str, result))
    else:
        result = json.dumps(result, indent=indent, sort_keys=True, ensure_ascii=False)

    output_file.write(result)
    output_file.write('\n')


def record(
    procfile_list,
    database_file,
    interval,
    environment=None,
    query=None,
    recnum=None,
    reevalnum=None,
):
    readers = {k: v for k, v in procfile.registry.items() if k in procfile_list}
    tree = proctree.Tree(readers)

    count = 1
    query_tpl = string.Template(query)
    with procrec.SqliteStorage(database_file, procfile_list, utility.get_meta()) as store:
        while True:
            start = time.time()
            if (
                query_tpl.template
                and environment
                and (count == 1 or reevalnum and (count + 1) % reevalnum == 0)
            ):
                query = query_tpl.safe_substitute(utility.evaluate(environment))

            result = tree.get_root()
            if query:
                try:
                    result = jsonpyth.jsonpath(result, query, always_return_list=True)
                except jsonpyth.JsonPathSyntaxError as ex:
                    raise CommandError(str(ex)) from ex

            store.record(start, proctree.flatten(result, procfile_list))

            count += 1
            if recnum and count > recnum:
                break

            latency = time.time() - start
            time.sleep(max(0, interval - latency))


def _get_file_queries(filenames: list):
    for filename in filenames:
        with open(filename, 'r') as f:
            yield procret.Query(f.read(), 'Custom query')

def _get_expr_queries(exprs: list):
    for expr in exprs:
        yield procret.create_query(expr, 'Custom expression')

def _get_named_queries(names: list):
    for query_name in names:
        try:
            query = procret.registry[query_name]
        except KeyError:
            raise CommandError(f'Unknown query {query_name}')
        else:
            yield query

def _get_pid_series_points(
    timeseries: list,
    epsilon: float = None,
    moving_average_window: int = None,
) -> dict:
    pid_series = {}
    for pid, series in itertools.groupby(timeseries, lambda r: r['pid']):
        pid_series[pid] = [(r['ts'], r['value']) for r in series]
        if epsilon:
            pid_series[pid] = utility.decimate(pid_series[pid], epsilon)
        if moving_average_window:
            x, y = zip(*pid_series[pid])
            pid_series[pid] = list(zip(
                utility.moving_average(x, moving_average_window),
                utility.moving_average(y, moving_average_window),
            ))

    return pid_series

def plot(
    database_file: str,
    plot_file: str,
    query_name_list: list = None,
    after: datetime = None,
    before: datetime = None,
    pid_list: list = None,
    epsilon: float = None,
    moving_average_window: int = None,
    logarithmic: bool = False,
    style: str = None,
    formatter: str = None,
    title: str = None,
    custom_query_file_list: list = None,
    custom_value_expr_list: list = None,
):
    queries = []
    if query_name_list:
        queries.extend(_get_named_queries(query_name_list))
    if custom_value_expr_list:
        queries.extend(_get_expr_queries(custom_value_expr_list))
    if custom_query_file_list:
        queries.extend(_get_file_queries(custom_query_file_list))

    if not (0 < len(queries) <= 2):
        raise CommandError('No or more than 2 queries to plot')

    for i, query in enumerate(queries):
        if title:
            queries[i] = query._replace(title=title)
        elif len(queries) > 1:
            queries[i] = query._replace(title=f'{queries[0].title} vs {queries[1].title}')

    pid_series_list = []
    for query in queries:
        timeseries = procret.query(database_file, query, after, before, pid_list)
        pid_series_list.append(_get_pid_series_points(timeseries, epsilon, moving_average_window))

    utility.plot(
        plot_file=plot_file,
        title=queries[0].title,
        pid_series1=pid_series_list[0],
        pid_series2=pid_series_list[1] if len(pid_series_list) > 1 else None,
        logarithmic=logarithmic,
        style=style,
        formatter=formatter,
    )


async def _forward_stream(stream_reader: asyncio.StreamReader, number: int, level: int):
    async for line in stream_reader:
        logger.log(level, '№%d: %s', number, line.strip().decode())

async def _create_process(cmd: str, number: int) -> asyncio.subprocess.Process:
    logger.debug('Starting №%d: %s', number, cmd)
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    asyncio.ensure_future(_forward_stream(process.stdout, number, logging.INFO))
    asyncio.ensure_future(_forward_stream(process.stderr, number, logging.WARNING))
    return process

async def _watch(
    interval: float,
    command_list: list,
    procfile_list: list,
    environment: list = None,
    query_list: list = None,
    repeat: int = None,
):
    readers = {k: v for k, v in procfile.registry.items() if k in procfile_list}
    tree = proctree.Tree(readers)

    count = 1
    process_list = []
    while True:
        start = time.time()
        result_command_list = _evaluate_command_list(tree, command_list, environment, query_list)
        if not process_list:
            process_list.extend(await asyncio.gather(
                *[_create_process(cmd, i + 1) for i, cmd in enumerate(result_command_list)]
            ))
        else:
            restart_list = []
            for i, p in enumerate(process_list):
                if p.returncode is not None:
                    logger.info('№%d exited with code %d, restarting', i + 1, p.returncode)
                    restart_list.append((i, _create_process(result_command_list[i], i + 1)))

            if restart_list:
                restart_indices, restart_coroutines = zip(*restart_list)
                for i, process in zip(restart_indices, await asyncio.gather(*restart_coroutines)):
                    process_list[i] = process

        latency = time.time() - start
        await asyncio.sleep(max(0, interval - latency))

        count += 1
        if repeat and count > repeat:
            break

def _evaluate_command_list(
    tree: proctree.Tree,
    command_list: list,
    environment: list = None,
    query_list: list = None,
):
    env_dict = {}

    if environment:
        env_dict.update(utility.evaluate(environment))

    if query_list:
        tree_root = tree.get_root()
        for query_name, query in query_list:
            query = string.Template(query).safe_substitute(env_dict)
            try:
                query_result = jsonpyth.jsonpath(tree_root, query, always_return_list=True)
            except jsonpyth.JsonPathSyntaxError as ex:
                raise CommandError(str(ex)) from ex

            if not query_result:
                logger.warning('Query %s evaluated empty', query_name)

            env_dict[query_name] = ','.join(map(str, query_result))

    return [string.Template(command).safe_substitute(env_dict) for command in command_list]

def _stop_process_tree(stop_signal: signal.Signals):
    """
    Interrupt any descendant of current process by sending SIGINT.

    In case procpath is running in foreground Ctrl+C causes
    SIGINT to be sent to all processing in its tree. But when
    it's in background it's not the case, so the tree has to
    be terminated.
    """

    tree = proctree.Tree({'stat': procfile.registry['stat']}, skip_self=False)
    query = '$..children[?(@.stat.ppid == {})]..stat.pid'.format(os.getpid())
    for pid in jsonpyth.jsonpath(tree.get_root(), query, always_return_list=True):
        with contextlib.suppress(ProcessLookupError):
            os.kill(pid, stop_signal)

def watch(stop_signal: str, **kwargs):
    stop_signal = signal.Signals[stop_signal]
    # In py37+ use asyncio.run
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_watch(**kwargs))
    except KeyboardInterrupt:
        _stop_process_tree(stop_signal)

        try:
            all_tasks = asyncio.all_tasks  # py37+
        except AttributeError:
            all_tasks = asyncio.Task.all_tasks
        task_list = asyncio.gather(*all_tasks(loop), return_exceptions=True)
        task_list.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            loop.run_until_complete(task_list)
    else:
        _stop_process_tree(stop_signal)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
