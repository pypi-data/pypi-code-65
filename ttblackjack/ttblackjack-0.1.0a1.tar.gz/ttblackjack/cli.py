import argparse
import webbrowser
from ttblackjack.game import Game
from ttblackjack import CONFIG
from ttblackjack import __version__, CONFIG_FP


def cmd_run():
    game = Game.from_config(CONFIG)
    game.welcome()
    game.run()


def cmd_config():
    print('Edit and save config file.')
    webbrowser.open(CONFIG_FP.as_uri())


def cli(args=None):
    parser = argparse.ArgumentParser(
        prog='ttblackjack',
        description='A blackjack game.',
        epilog='Have a nice game.'
    )

    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))

    subparsers = parser.add_subparsers(help='sub-command help')
    parser_a = subparsers.add_parser('run', help='help run')
    parser_a.add_argument('cmd', action='store_const', const=cmd_run)

    parser_b = subparsers.add_parser('config', help='help config')
    parser_b.add_argument('cmd', action='store_const', const=cmd_config)

    parser_c = subparsers.add_parser('help', help='help help')
    parser_c.add_argument('cmd', action='store_const', const=parser.print_help)

    args = parser.parse_args(args)

    if not hasattr(args, 'cmd'):
        parser.print_help()
        parser.exit(0)

    return args


def main():
    command = cli()
    command.cmd()
