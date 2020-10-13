# -*- coding: utf-8 -*-
import argparse
import errno
from pathlib import Path

import pkg_resources

from arkindex_cli.commands.benchmark import add_benchmark_parser
from arkindex_cli.commands.classes import add_classes_parser
from arkindex_cli.commands.imports import add_import_parser
from arkindex_cli.commands.login import add_login_parser
from arkindex_cli.commands.secrets import add_secrets_parser


def get_version():
    version_file = Path(__file__).absolute().parent / "VERSION"
    if version_file.is_file():
        with version_file.open():
            return version_file.read().strip()
    else:
        try:
            return pkg_resources.get_distribution("arkindex-cli").version
        except pkg_resources.ResolutionError:
            pass


def get_parser():
    parser = argparse.ArgumentParser(description="Arkindex command-line tool")
    parser.add_argument(
        "-p",
        "--profile",
        dest="profile_slug",
        metavar="SLUG",
        help="Slug of an Arkindex profile to use instead of the default.",
    )

    version = get_version()
    if version:
        parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"%(prog)s {version}",
        )

    subcommands = parser.add_subparsers(metavar="subcommand")

    add_login_parser(subcommands)
    add_import_parser(subcommands)
    add_benchmark_parser(subcommands)
    add_classes_parser(subcommands)
    add_secrets_parser(subcommands)

    return parser


def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    if "func" in args:
        # Run the subcommand's function
        try:
            status = args.pop("func")(**args)
            parser.exit(status=status)
        except KeyboardInterrupt:
            # Just quit silently on ^C instead of displaying a long traceback
            parser.exit(status=errno.EOWNERDEAD)
    else:
        parser.error("A subcommand is required.")
