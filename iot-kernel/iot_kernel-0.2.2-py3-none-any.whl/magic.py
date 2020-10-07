#!/usr/bin/env python3

from iot_device import Config

from .output import Output
from .pip import Pip
from .kernel_logger import logger
from .argparser_fix import ArgumentParserFix, ParserError
import logging
import shlex
import time
import re


"""
Wrappers for declaring magic.
"""

# dictionaries of handlers name --> method
LINE_MAGIC = {}


def line_magic(name, doc=None):

    def real_decorator(function):

        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
        LINE_MAGIC[name] = (wrapper, doc)
        return wrapper

    return real_decorator


@line_magic("to_host", "Copy variables from MCU to host")
def tohost_magic(kernel, args):

    class Output:
        def __init__(self):
            self._ans = ''
            self._err = ''

        def fmt(self, value):
            if not value: return
            if isinstance(value, bytes): value = value.decode()
            value = str(value)
            value = value.replace('\r', '')
            value = value.replace('\x04', '')
            return value

        def ans(self, value):
            if value:
                self._ans += self.fmt(value)

        def err(self, value):
            if value:
                self._err += self.fmt(value)

    pattern = re.compile(r"^\s+|\s*[, ]\s*|\s+$")
    for var in [x for x in pattern.split(args) if x]:
        out = Output()
        kernel.repl.eval(f"import json\nprint(json.dumps(repr({var})))", out)
        if len(out._err.strip()) > 0:
            kernel.error(f"Variable '{var}': {out._err}\n")
            return
        logger.debug(f"{var} = {out._ans}")
        kernel.execute_ipython(f"{var} = eval({out._ans})\n")


@line_magic("config", "List configuration in mcu/config.py")
def config_magic(kernel, args):
    verbose = '-v' in args
    if verbose:
        kernel.print("Configuration Variables:\n")
    for k, v in Config.config().items():
        skip = [ 'password', 'hosts', 'uid', 'wifi_ssid', 'wifi_pwd', 'sys' ]
        if any(x in k for x in skip):
            continue
        kernel.print("{:20} {}\n".format(k, v))
    if not verbose:
        return
    kernel.print("\nHosts:\n")
    hosts = Config.get_config(file='hosts.py').get('hosts', {})
    for k, v in hosts.items():
        name = v
        if isinstance(v, dict):
            name = v.get('name')
        kernel.print(f"{name:20} {k}\n")


@line_magic("softreset", "Reset MCU")
def softreset_magic(kernel, args):
    kernel.repl.softreset()
    if '-q' in args:
        return
    kernel.print("\n")
    kernel.print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", 'white', 'on_red')
    kernel.print("!!!!!      softreset      !!!!!\n", 'white', 'on_red')
    kernel.print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", 'white', 'on_red')
    kernel.print("\n")


@line_magic("uid", "Read UID from microcontroller")
def uid_magic(kernel, _):
    kernel.print(kernel.repl.uid)


@line_magic("sync_time", "Synchronize microcontroller time to host")
def sync_time_magic(kernel, _):
    kernel.repl.sync_time()


@line_magic("get_time", "Query microcontroller time")
def get_time_magic(kernel, _):
    t = time.mktime(kernel.repl.get_time())
    kernel.print(f"{time.strftime('%Y-%b-%d %H:%M:%S', time.localtime(t))}\n")


@line_magic("discover", "Discover available MCUs")
def discover_magic(kernel, args):
    kernel.discover.scan()
    with kernel.discover as devices:
        for dev in devices:
            kernel.print(f"{Config.uid2hostname(dev.uid)} ({dev.uid})")


@line_magic("connect", "connect hostname")
def connect_magic(kernel, hostname):
    """
    %connect HOSTNAME
    """
    uid = Config.hostname2uid(hostname)
    if not uid: uid = hostname
    kernel.print(f"{hostname} --> {uid}")
    dev = kernel.discover.get_device(uid)
    if not dev:
        kernel.discover.scan()
        dev = kernel.discover.get_device(uid)
    if not dev:
        kernel.Error(f"Device not available: {hostname}")
    else:
        kernel.device = dev
        kernel.print(dev)


@line_magic("lsmagic", "IoT-Python specific magic functions")
def ls_magic(kernel, _):
    kernel.print("Line Magic:\n")
    for k, v in sorted(LINE_MAGIC.items()):
        if not v[1]: continue
        kernel.print("  %{:20s}  {}\n".format(k, v[1]))
    kernel.print("\nCell Magic:\n")
    kernel.print("  %%{:19s}  {}\n".
        format('mcu', "Evaluate on mcu(s)"))
    kernel.print("  %%{:19s}  {}\n".
        format('host', "Pass cell to iPython for evaluation"))


@line_magic("loglevel", "Set IoT Python Kernel log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
def loglevel_magic(kernel, args):
    try:
        logging.basicConfig(level=args)
        logger.setLevel(args)
        logger.info("set logger level to '{}'".format(args))
    except ValueError as e:
        kernel.error(f"{e}\n")


@line_magic("rlist", "List files on MCU")
def rlist_magic(kernel, args):
    kernel.repl.rlist(Output(kernel))


@line_magic("rsync", "Synchronize MCU to host directories")
def rsync_magic(kernel, args):
    parser = ArgumentParserFix(description='Synchronize files on MCU to host')
    parser.add_argument('path', nargs='?', default='/')
    parser.add_argument('-p', '--projects', nargs='*', default="base", help="host directories")
    parser.add_argument('-d', '--dry_run', action='store_true', help="report changes but do not commit")
    try:
        args = parser.parse_args(shlex.split(args))
        kernel.repl.rsync(Output(kernel), path=args.path, projects=args.projects, dry_run=args.dry_run)
    except ParserError as e:
        kernel.error(f"{e}\n")


@line_magic("rput", "Copy file from host to MCU")
def rput_magic(kernel, args):
    parser = ArgumentParserFix(description='Copy file from host to MCU')
    parser.add_argument('path')
    parser.add_argument('-p', '--project', default='base')
    try:
        args = parser.parse_args(shlex.split(args))
        with kernel.mcu as op:
            op.fput(args.project, args.path)
    except ParserError as e:
        kernel.error(f"{e}\n")


@line_magic("rget", "Copy file from MCU to host")
def rget_magic(kernel, args):
    parser = ArgumentParserFix(description='Copy file from MCU to host')
    parser.add_argument('path')
    parser.add_argument('-p', '--project', default='base')
    try:
        args = parser.parse_args(shlex.split(args))
        with kernel.mcu as op:
            op.fget(args.project, args.path)
    except ParserError as e:
        kernel.error(f"{e}\n")


@line_magic("rcat", "Print contents of file on MCU")
def rcat_magic(kernel, args):
    kernel.repl.cat(Output(kernel), args)
    kernel.print('\n')


@line_magic("rdelete", "redelete [-r] path: remove files on MCU")
def rdelete_magic(kernel, args):
    parser = ArgumentParserFix(description='Remove files or directories')
    parser.add_argument('path')
    parser.add_argument('-r', '--recursive', action='store_true')
    try:
        args = parser.parse_args(shlex.split(args))
        with kernel.mcu as op:
            res = op.rm_rf(args.path, args.recursive)
            if not res:
                kernel.error(f"***** '{args.path}' not deleted")
    except ParserError as e:
        kernel.error(f"{e}\n")


@line_magic("pip", "Install packages from PyPi")
def pip_magic(kernel, args):
    parser = ArgumentParserFix(description='Install package from PyPi.org')
    parser.add_argument('operation', choices=['install'])
    parser.add_argument('package')
    parser.add_argument('-p', '--project', default=kernel.mcu.projects[-1], help="sub-folder in ~/mcu")
    try:
        args = parser.parse_args(shlex.split(args))
        pip = Pip(Config.get('host_dir', '~/mcu'), args.project, Output(kernel))
        pip.install(args.package)
    except ParserError as e:
        kernel.error(f"{e}\n")


####################################################################################
# Debugging only, remove when done

@line_magic("mcu_files")
def mcu_files_magic(kernel, args):
    kernel.repl.mcu_files(Output(kernel), args)

@line_magic("host_files")
def host_files_magic(kernel, args):
    for f, v in kernel.repl.host_files(args, ['base', 'test']).items():
        kernel.print(f"{f}: {v}\n")

@line_magic("diff")
def diff_magic(kernel, args):
    a, d, u = kernel.repl.rdiff(args, ['base', 'test'])
    for x in a: kernel.print(f"ADD     {x}\n")
    for x in d: kernel.print(f"DELETE  {x}\n")
    for x in u: kernel.print(f"UPDATE  {x}\n")
