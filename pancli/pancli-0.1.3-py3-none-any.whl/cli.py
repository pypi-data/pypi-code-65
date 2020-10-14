import sys
import argparse
from pancli.commands.package import PackageCommand
from pancli.commands.crawl import CrawlCommand
from pancli.commands.plugin import PluginCommand
from pancli.commands.list import ListCommand
from pancli.commands.settings import SettingsCommand
from pancli.commands.deploy import DeployCommand
from pancli import __version__ as version

cmds = {
    'package': PackageCommand(),
    'crawl': CrawlCommand(),
    'plugin': PluginCommand(),
    'list': ListCommand(),
    'settings': SettingsCommand(),
    'deploy': DeployCommand()
}


def _pop_command_name(argv):
    i = 0
    for arg in argv[1:]:
        if not arg.startswith('-'):
            del argv[i]
            return arg
        i += 1


def main(argv = None):
    if argv is None:
        argv = sys.argv

    usage = '%(prog)s command\r\n'
    usage += 'Available commands: \r\n'
    for available_command in cmds.keys():
        usage += '\t%s\r\n' % available_command
    
    parser = argparse.ArgumentParser('pancli', usage=usage)
    parser.add_argument('-V', '--version', action='version', default=False,
                    version='%(prog)s {version}'.format(version=version))
    
    command = _pop_command_name(argv)

    if command is None:
        ops = parser.parse_args()
        if not command and ops.version:
            print('pancli %s' % version)
            sys.exit(0)

        print('Please specify command.')
        parser.print_help()
        sys.exit(1)

    try:
        cmd = cmds[command]
    except KeyError:
        print(f"Invalid command {command}")
        sys.exit(1)
    
    cmd.add_arguments(parser)
    parser.usage = f'pansi {command}'
    args = parser.parse_args()
    cmd.run(args)


if __name__ == '__main__':
    main()