import os
import logging
from . import CommandBase
from ..plugin import list_, _pip_install, install_plugin, ensure_plugin


def init_logging(config=None, log_level=1):
    log_level = [logging.ERROR, logging.INFO, logging.DEBUG][log_level]
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(log_level)


class PluginCommand(CommandBase):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand')

        parser_list = subparsers.add_parser('list')                        

        parser_install = subparsers.add_parser('install')
        parser_install.add_argument('url_or_path')
        parser_install.add_argument('-v', '--verbose', action='count', default=0)


    def run(self, args):
        if args.subcommand == 'list':
            return list_()
        if args.subcommand == 'install':
            init_logging(log_level=args.verbose)
            return ensure_plugin(args.url_or_path)