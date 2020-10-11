import argparse
import logging
import shutil
import sys
from datetime import datetime, timezone

from . import command, procfile, procret, __version__


logger = logging.getLogger(__package__)


def add_query_parser(parent):
    parser = parent.add_parser('query', formatter_class=HelpFormatter, description='''
        Execute given JSONPath query against process tree producing JSON or
        separator-delimited values.
    ''')
    parser.add_argument(
        'query',
        nargs='?',
        help='''
            JSONPath expression, for example this query returns
            PIDs for process subtree including the given root's:

            $..children[?(@.stat.pid == 2610)]..pid
        '''
    )
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-f', '--procfile-list',
        default='stat, cmdline',
        type=lambda s: list(map(str.strip, s.split(','))),
        help=f'''
            Procfs files to read per PID.  Comma-separated list. By default: %(default)s.
            Available: {', '.join(procfile.registry.keys())}.
        ''',
    )
    arguments.add_argument(
        '-d', '--delimiter',
        help='Join query result using given delimiter',
    )
    arguments.add_argument(
        '-i', '--indent',
        type=int,
        help='Format result JSON using given indent number',
    )
    parser.set_defaults(output_file=sys.stdout)


def add_record_parser(parent):
    parser = parent.add_parser('record', formatter_class=HelpFormatter, description='''
        Record the nodes of process tree matching given JSONPath query into a SQLite
        database in given intervals.
    ''')
    parser.add_argument(
        'query',
        nargs='?',
        help='''
            JSONPath expression, for example this query returns
            a node including its subtree for given PID:

            $..children[?(@.stat.pid == 2610)]
        '''
    )
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-f', '--procfile-list',
        default='stat, cmdline',
        type=lambda s: list(map(str.strip, s.split(','))),
        help=f'''
            Procfs files to read per PID.  Comma-separated list. By default: %(default)s.
            Available: {', '.join(procfile.registry.keys())}.
        ''',
    )
    arguments.add_argument(
        '-e', '--environment',
        action='append',
        type=lambda s: s.split('=', 1),
        help='''
            Commands to evaluate in the shell and template the query, like VAR=date.
            Multiple occurrence possible.
        ''',
    )
    arguments.add_argument(
        '-d', '--database-file',
        required=True,
        help='Path to the recording database file',
    )
    loop_control = parser.add_argument_group('loop control arguments')
    loop_control.add_argument(
        '-i', '--interval',
        type=float,
        default='10',
        help='Interval in second between each recording, %(default)s by default.',
    )
    loop_control.add_argument(
        '-r', '--recnum',
        type=int,
        help='''
            Number of recordings to take at --interval seconds apart.
            If not specified, recordings will be taken indefinitely.
        ''',
    )
    loop_control.add_argument(
        '-v', '--reevalnum',
        type=int,
        help='''
            Number of recordings after which environment must be re-evaluate.
            It's useful when you expect it to change in while recordings are
            taken.
        ''',
    )


def add_plot_parser(parent):
    parser = parent.add_parser('plot', formatter_class=HelpFormatter, description='''
        Plot previously recorded SQLite database using predefined or custom SQL
        expression or query.
    ''')
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-d', '--database-file',
        required=True,
        help='Path to the database file to read from.',
    )
    arguments.add_argument(
        '-f', '--plot-file',
        default='plot.svg',
        help='Path to the output SVG file, plot.svg by default.',
    )
    query_control = parser.add_argument_group('query control arguments')
    query_control.add_argument(
        '-q', '--query-name',
        action='append',
        dest='query_name_list',
        help=f'''
            Built-in query name. Available: {",".join(procret.registry.keys())}.
            Can occur once or twice (including other query-contributing options).
            In the latter case, the plot has two Y axes.
        ''',
    )
    query_control.add_argument(
        '--custom-query-file',
        action='append',
        dest='custom_query_file_list',
        help='''
            Use custom SQL query in given file.
            The result-set must have 3 columns: ts, pid, value. See procpath.procret.
            Can occur once or twice (including other query-contributing options).
            In the latter case, the plot has two Y axes.
        ''',
    )
    query_control.add_argument(
        '--custom-value-expr',
        action='append',
        dest='custom_value_expr_list',
        help='''
            Use custom SELECT expression to plot as the value.
            Can occur once or twice (including other query-contributing options).
            In the latter case, the plot has two Y axes.
        ''',
    )
    filter_control = parser.add_argument_group('filter control arguments')
    filter_control.add_argument(
        '-a', '--after',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc),
        help='Include only points after given UTC date, like 2000-01-01T00:00:00.',
    )
    filter_control.add_argument(
        '-b', '--before',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc),
        help='Include only points before given UTC date, like 2000-01-01T00:00:00.',
    )
    filter_control.add_argument(
        '-p', '--pid-list',
        type=lambda s: list(map(int, s.split(','))),
        help='Include only given PIDs. Comma-separated list.',
    )
    plot_control = parser.add_argument_group('plot control arguments')
    plot_control.add_argument(
        '-l', '--logarithmic',
        action='store_true',
        help='Plot using logarithmic scale.',
    )
    plot_control.add_argument(
        '--style',
        help='Plot using given pygal.style, like LightGreenStyle.',
    )
    plot_control.add_argument(
        '--formatter',
        help='Force given pygal.formatter, like integer.',
    )
    plot_control.add_argument(
        '--title',
        help='Override plot title.',
    )
    postprocessing_control = parser.add_argument_group('post-processing control arguments')
    postprocessing_control.add_argument(
        '-e', '--epsilon',
        type=float,
        help='Reduce points using Ramer-Douglas-Peucker algorithm and given ε.',
    )
    postprocessing_control.add_argument(
        '-w', '--moving-average-window',
        type=int,
        help='Smooth the lines using moving average.',
    )


def add_watch_parser(parent):
    parser = parent.add_parser('watch', formatter_class=HelpFormatter, description='''
        Execute given commands in given intervals. It has similar purpose to
        procps watch, but allows JSONPath queries to process tree to choose
        processes of interest.
    ''')
    cmd_control = parser.add_argument_group('command control arguments')
    cmd_control.add_argument(
        '-e', '--environment',
        action='append',
        type=lambda s: s.split('=', 1),
        help='''
            Commands to evaluate in the shell, like
            C1='docker inspect -f "{{.State.Pid}}" nginx' or D='date +%%s'.
            Multiple occurrence possible.
        ''',
    )
    cmd_control.add_argument(
        '-q', '--query',
        action='append',
        dest='query_list',
        type=lambda s: s.split('=', 1),
        help='''
            JSONPath expressions that typically evaluate into a list of PIDs.
            The environment defined with -e can be used like
            L1='$..children[?(@.stat.pid == $C1)]..pid'.
            Multiple occurrence possible.
        ''',
    )
    cmd_control.add_argument(
        '-c', '--command',
        required=True,
        dest='command_list',
        action='append',
        help='''
            Target command to "watch" in the shell. The environment and query
            results can be used like 'smemstat -o smemstat-$D.json -p $L1'.
            Query result lists are joined with comma. Multiple occurrence
            possible.
        ''',
    )
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-i', '--interval',
        required=True,
        type=float,
        help='''
            Interval in second after which to re-evaluate the environment and the
            queries, and re-run each command if one has finished.
        ''',
    )
    arguments.add_argument(
        '-r', '--repeat',
        type=int,
        help='Fixed number to repetitions instead of infinite watch.',
    )
    arguments.add_argument(
        '-s', '--stop-signal',
        type=str,
        default='SIGINT',
        help='Signal to send to the spawned processes on watch stop. By default: %(default)s.',
    )
    arguments.add_argument(
        '-f', '--procfile-list',
        default='stat, cmdline',
        type=lambda s: list(map(str.strip, s.split(','))),
        help=f'''
            Procfs files to read per PID.  Comma-separated list. By default: %(default)s.
            Available: {', '.join(procfile.registry.keys())}.
        ''',
    )


class HelpFormatter(argparse.HelpFormatter):

    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None):
        if not width:
            width = min(100, shutil.get_terminal_size((80, 20)).columns)

        super().__init__(prog, indent_increment, max_help_position, width)

    def _format_usage(self, usage, actions, groups, prefix):
        banner = (
            r'     ___   ___   ___   __    ___    __   _____  _   ''\n'
            r'    | |_) | |_) / / \ / /`  | |_)  / /\   | |  | |_|''\n'
            r'    |_|   |_| \ \_\_/ \_\_, |_|   /_/--\  |_|  |_| |''\n\n'
            r'                   a process tree analysis workbench''\n'
        )
        result = super()._format_usage(usage, actions, groups, prefix)
        if actions:
            result = '{}\n{}'.format(banner, result)

        return result

    def _get_default_metavar_for_optional(self, action):
        return action.option_strings[-1].strip('-').upper()


def build_parser():
    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)

    cmd_funcs = add_query_parser, add_record_parser, add_plot_parser, add_watch_parser
    parent = parser.add_subparsers(dest='command')
    [fn(parent) for fn in cmd_funcs]

    return parser


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-7s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    parser = build_parser()
    kwargs = vars(parser.parse_args())
    # "required" keyword argument to add_subparsers() was added in py37
    if not kwargs.get('command'):
        parser.error('the following arguments are required: command')

    try:
        getattr(command, kwargs.pop('command'))(**kwargs)
    except KeyboardInterrupt:
        pass
    except command.CommandError as ex:
        logger.error(ex)
        sys.exit(1)
