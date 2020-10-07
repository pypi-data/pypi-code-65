#!python
# Copyright 2020 Grid AI Inc.
"""Entrypoint for the Grid CLI."""
import click

import grid.cli as cli
import grid.globals as env

from grid.metadata import __version__
from grid.utilities import introspect_module


@click.group()
@click.option(
    '--debug',
    type=bool,
    help='Used for logging additional information for debugging purposes.',
    is_flag=True)
def main(debug: bool = True) -> None:
    """Grid CLI"""
    if debug:
        env.logger.info('Starting gridrunner in DEGUB mode.')

    env.DEBUG = debug


@main.command()
def version() -> None:
    """
    Prints CLI version to stdout
    """
    click.echo(__version__)


#  Adds all CLI commands. Commands are introspected
#  from the cli module.
for command in introspect_module(cli):
    main.add_command(command)

if __name__ == '__main__':
    main()
