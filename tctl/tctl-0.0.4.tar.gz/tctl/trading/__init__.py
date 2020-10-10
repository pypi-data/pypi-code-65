#!/usr/bin/env python

import click
from .. import utils
from . import crud


COMMANDS = ["ls", "list"]


def options_validator(ctx, param, args):
    if len(args) == 0 or args[0] not in COMMANDS:
        raise click.UsageError(
            "Command shoule be one of:\n  - {commands}".format(
                commands='\n  - '.join(COMMANDS)))

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
    command, options = options

    if command in ["ls", "list"]:
        crud.positions_list(options)


# router function
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('options', nargs=-1, type=click.UNPROCESSED,
                callback=options_validator)
def trades(options):
    command, options = options

    if command in ["ls", "list"]:
        crud.trades_list(options)
