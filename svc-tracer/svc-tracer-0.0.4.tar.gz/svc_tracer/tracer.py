# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import sys
import logging

from .sniffer import Sniffer
from .printer import MessagePrinter, PairedPrinter, PrintOptions

VALID_LEVELS = 'debug, info, warn, error'
VALID_PARTS = 'header, data, all, none'
VALID_TRANSPORTS = 'auto, buffered, framed'
VALID_PROTOCOLS = 'auto, binary, compact, json'


def get_flags():  # pragma: no cover
  # general options
  def add_common_argument(cmd):
    cmd.add_argument('-i', '--iface', type=str, required=True, metavar='<iface>',
                     help='The interface of sniff from')
    cmd.add_argument('-p', '--port', type=int, required=True, metavar='<port>',
                     help='The port of the service listens to')
    cmd.add_argument('-f', '--from', type=str, nargs='+', metavar='<ip>',
                     help='Only record the messages from this IP(s)')
    cmd.add_argument('-t', '--to', type=str, nargs='+', metavar='<ip>',
                     help='Only record the messages to this IP(s)')
    cmd.add_argument('-m', '--method', type=str, nargs='+', metavar='<regex>',
                     help='Only record the messages match this method(s)')
    cmd.add_argument('--unpaired', default=False, action='store_true',
                     help='Print the messages as they arrive, possibly out of order')
    cmd.add_argument('--print', type=str, default='all', metavar='<mode>',
                     help='Print parts of the message. Options: %s' % VALID_PARTS)
    cmd.add_argument('--check_interval', type=int, default=5, metavar='<interval>',
                     help='Interval in seconds for checking unpair message')
    cmd.add_argument('--check_timeout', type=int, default=5, metavar='<timeout>',
                     help='Timeout in seconds for checking unpair alert')
    cmd.add_argument('-l', '--log-level', type=str, default='info', metavar='<level>',
                     help='The output level of messages. Options: %s' % VALID_LEVELS)
    cmd.add_argument('-o', '--log-file', type=str, default=None, metavar='<path>',
                     help='The output file of messages')
    cmd.add_argument('-c', '--log-clear', default=False, action='store_true',
                     help='The output file will be cleared')

  import os
  os.environ['COLUMNS'] = "132"
  p = argparse.ArgumentParser()
  cmds = p.add_subparsers(dest='cmd')

  # subcommand: show iface list
  cmds.add_parser('show', help='Show all interfaces')

  # subcommand: trace thrift service
  thrift = cmds.add_parser('thrift', help='Trace thrift service')
  add_common_argument(thrift)
  thrift.add_argument('--transport', type=str, default='auto', metavar='<trans>',
                      help='Use a specific transport. Options: %s' % VALID_TRANSPORTS)
  thrift.add_argument('--protocol', type=str, default='auto', metavar='<proto>',
                      help='Use a specific protocol. Options: %s' % VALID_PROTOCOLS)
  thrift.add_argument('--finagle', default=False, action='store_true',
                      help='Detect finagle-thrift traffic (i.e.: with request headers)')
  thrift.add_argument('--idl-file', type=str, default=None, metavar='<path>',
                      help='Use .thrift file to resolve types')

  # subcommand: trace http service
  http = cmds.add_parser('http', help="Trace http service")
  add_common_argument(http)

  return p, p.parse_args()


def show_iface():
  import platform
  system = platform.system()
  print("Available interfaces:")
  if system == 'Windows':
    from scapy.arch.windows import show_interfaces
    show_interfaces()
  elif system == 'Linux':
    from scapy.arch.linux import get_if_list
    print(get_if_list())
  else:
    import os
    print(os.system('ifconfig'))


def main():
  # route to the subcommand
  parser, flags = get_flags()
  if flags.cmd == 'show':
    show_iface()
    sys.exit(1)
  elif flags.cmd == 'thrift':
    kwargs = {
      "message": flags.cmd,
      "transport": flags.transport,
      "protocol": flags.protocol,
      "finagle": flags.finagle,
      "idl_file": flags.idl_file,
    }
  elif flags.cmd == 'http':
    kwargs = {
      "message": flags.cmd,
    }
  elif flags.cmd:
    print('Unknown command: %s' % flags.cmd)
    parser.print_help()
    sys.exit(2)
  else:
    parser.print_help()
    sys.exit(3)

  # setup logger
  logger = logging.getLogger()
  logger.addHandler(logging.StreamHandler(sys.stdout))
  if flags.log_file:
    logger.addHandler(logging.FileHandler(flags.log_file, 'a' if flags.log_clear else 'w'))
  [x.setFormatter(logging.Formatter('[%(levelname)s] %(message)s')) for x in logger.handlers]
  if flags.log_level.lower() == 'debug':
    logger.setLevel(logging.DEBUG)
  elif flags.log_level.lower() == 'info':
    logger.setLevel(logging.INFO)
  elif flags.log_level.lower() == 'warn':
    logger.setLevel(logging.WARN)
  elif flags.log_level.lower() == 'error':
    logger.setLevel(logging.ERROR)
  else:
    print('Unknown log level: %s' % flags.log_level)
    print('Valid options for --log-level are: %s' % VALID_LEVELS)
    sys.exit(10)

  # setup message printer
  cls = MessagePrinter if flags.unpaired else PairedPrinter
  printer = cls(PrintOptions(
    port=flags.port,
    from_ip=getattr(flags, 'from'),
    to_ip=getattr(flags, 'to'),
    methods=flags.method,
    show_header=flags.print == 'header' or flags.print == 'all',
    show_data=flags.print == 'data' or flags.print == 'all',
  ))

  # setup sniffer and loop forever
  kwargs['log_level'] = logger.level
  sniffer = Sniffer(flags.iface, flags.port, printer, **kwargs)
  logging.info("Start to sniff %s messages on iface '%s' and port '%d'..." % (flags.cmd, flags.iface, flags.port))

  try:
    while sniffer.is_alive():
      sniffer.join(flags.check_interval)
      if hasattr(printer, 'timer') and callable(getattr(printer, 'timer')):
          printer.timer(flags.check_timeout)
  except (KeyboardInterrupt, SystemExit):
    pass

  sniffer.stop(wait_for_stopped=True)
  logging.info("Stop to sniff messages.")


if __name__ == '__main__':
  main()
