#!/usr/bin/env python

import click
import sys
from .. import utils
from . import crud


POSITIONS_COMMANDS = {
    "ls": "  Retreive position history (optional: --account, --strategy, --status, --start, --end)",
    "list": "Retreive position history (optional: --account, --strategy, --status, --start, --end)"
}

TRADES_COMMANDS = {
    "ls": "  Retreive trade history (optional: --account, --strategy, --status, --start, --end)",
    "list": "Retreive trade history (optional: --account, --strategy, --status, --start, --end)"
}


def options_validator(ctx, param, args):
    if sys.argv[1].lower() == "positions":
        COMMANDS = POSITIONS_COMMANDS
    elif sys.argv[1].lower() == "trades":
        COMMANDS = TRADES_COMMANDS

    if len(args) == 0 or args[0] not in COMMANDS:
        cmd = [f"{k}  {v}" for k, v in COMMANDS.items()]
        raise click.UsageError(
            "Command shoule be one of:\n\n - {commands}".format(
                commands='\n - '.join(cmd)))

    args = list(args)
    command = args[0]
    del args[0]

    optional = {}
    required = {}
    if command in ["ls", "list"]:
        optional = {
            "account": ["-a", "--account"],
            "strategy": ["-s", "--strategy"],
            "status": ["-statuses"],
            "start": ["--start"],
            "end": ["--end"],
        }

    args = utils.args_parser(args, required, optional)

    return command, args


@click.group()
def cli():
    pass


# router function
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('options', nargs=-1, type=click.UNPROCESSED,
                callback=options_validator)
def positions(options):
    """Retreive position history with filtering options"""
    command, options = options

    if command in ["ls", "list"]:
        crud.positions_list(options)


# router function
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('options', nargs=-1, type=click.UNPROCESSED,
                callback=options_validator)
def trades(options):
    """Retreive trade history with filtering options"""
    command, options = options

    if command in ["ls", "list"]:
        crud.trades_list(options)
