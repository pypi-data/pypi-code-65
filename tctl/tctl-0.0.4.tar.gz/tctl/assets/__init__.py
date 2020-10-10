#!/usr/bin/env python

import click
from .. import utils
from . import assets_crud
from . import exchanges_crud


COMMANDS = ["ls", "list", "show", "info", "bar", "bars", "calendar"]

def assets_options_validator(ctx, param, args):
    if len(args) == 0 or args[0] not in COMMANDS:
        raise click.UsageError(
            "Command shoule be one of:\n  - {commands}".format(
                commands='\n  - '.join(COMMANDS)))

    args = list(args)
    command = args[0]
    del args[0]

    flags = {}
    optional = {}
    required = {}

    if command in ["ls", "list", "show"]:
        flags = {
            "delisted": ["-d", "--delisted"],
        }

    elif command in ["info"]:
        required = {
            "asset": ["-a", "--asset"],
        }
        flags = {
            "history": ["-h", "--history"],
        }

    elif command in ["bar"]:
        required = {
            "asset": ["-a", "--asset"],
            "start": ["--start"],
        }
        optional = {
            "end": ["--end"],
        }

    return command, utils.args_parser(args, required, optional, flags)


def exchanges_options_validator(ctx, param, args):
    if len(args) == 0 or args[0] not in COMMANDS:
        raise click.UsageError(
            "Command shoule be one of:\n  - {commands}".format(
                commands='\n  - '.join(COMMANDS)))

    args = list(args)
    command = args[0]
    del args[0]

    flags = {}
    optional = {}
    required = {}

    if command in ["info"]:
        required = {
            "exchange": ["-e", "--exchange"],
        }
    elif command in ["calendar"]:
        required = {
            "exchange": ["-e", "--exchange"],
        }
        optional = {
            "start": ["--start"],
            "end": ["--end"],
        }
    return command, utils.args_parser(args, required, optional, flags)


@click.group()
def cli():
    pass


# asset router function
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('options', nargs=-1, type=click.UNPROCESSED,
                callback=assets_options_validator)
def assets(options):
    command, options = options

    if command in ["ls", "list"]:
        assets_crud.assets_list(options)

    elif command == "info":
        assets_crud.asset_info(options)

    elif command == "bar":
        assets_crud.asset_bar(options)

    elif command == "bars":
        # crud.asset_bars(options)
        click.echo(click.style("\nFAILED", fg="red") +" with status code 422:")
        click.echo("Due to licensing restrictions, you can only access US equity data from Tradologics servers (tradelets, research, etc)")


# asset router function
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('options', nargs=-1, type=click.UNPROCESSED,
                callback=exchanges_options_validator)
def exchanges(options):
    command, options = options

    if command in ["ls", "list"]:
        exchanges_crud.exchanges_list(options)

    if command in ["info"]:
        exchanges_crud.exchange_info(options)

    if command in ["calendar"]:
        exchanges_crud.exchange_calendar(options)
