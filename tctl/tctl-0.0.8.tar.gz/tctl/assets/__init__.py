#!/usr/bin/env python

import click
import sys
from .. import utils
from . import assets_crud
from . import exchanges_crud


ASSETS_COMMANDS = {
    "ls": "      Retreive supported assets list (optional: --delisted)",
    "list": "    Retreive supported assets list (optional: --delisted)",
    "info": "    Show asset information (via --asset|-a <ASSET>, optional: --history)",
}

BARS_COMMANDS = {
    "single": "  Create single bar (via --asset|-a <ASSET> --start <YYYY-MM-DD>, optional: --end <YYYY-MM-DD>)",
    "history": " Update historical bar data for certain assets tradehook (via --asset|-a <ASSET>)",
}

EXCH_COMMANDS = {
    "ls": "      Retreive supported exchange list",
    "list": "    Retreive supported exchange list",
    "info": "    Show exchange information (via --exchange|-e <EXCHANGE-MIC>)",
    "calendar": "Delete exchange calendar (via --exchange|-e <EXCHANGE-MIC>, optional: -start <YYYY-MM-DD>, --end <YYYY-MM-DD>)",
}


def assets_options_validator(ctx, param, args):
    if sys.argv[1].lower() == "assets":
        COMMANDS = ASSETS_COMMANDS
    elif sys.argv[1].lower() == "bars":
        COMMANDS = BARS_COMMANDS

    cmd = [f"{k}  {v}" for k, v in COMMANDS.items()]
    if len(args) == 0:
        click.echo("Usage: tctl {command} ACTION [OPTIONS]...".format(
            command=sys.argv[1]))
        click.echo("\nAvailable actions:\n\n - {commands}".format(
                commands='\n - '.join(cmd)))
        sys.exit(0)
    if args[0] not in COMMANDS:
        raise click.UsageError(
            "Action shoule be one of:\n\n - {commands}".format(
                commands='\n - '.join(cmd)))

    args = list(args)
    command = args[0]
    del args[0]

    flags = {}
    optional = {}
    required = {}

    if command in ["ls", "list"]:
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
    COMMANDS = EXCH_COMMANDS
    if len(args) == 0 or args[0] not in COMMANDS:
        cmd = [f"{k}  {v}" for k, v in COMMANDS.items()]
        raise click.UsageError(
            "Command shoule be one of:\n\n - {commands}".format(
                commands='\n - '.join(cmd)))

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
    """List assets with misc. filtering options"""
    command, options = options

    if command in ["ls", "list"]:
        assets_crud.assets_list(options)

    elif command == "info":
        assets_crud.asset_info(options)


# asset router function
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('options', nargs=-1, type=click.UNPROCESSED,
                callback=assets_options_validator)
def bars(options):
    """List pricing information for assets"""
    command, options = options

    if command == "single":
        assets_crud.asset_bar(options)

    elif command == "history":
        # crud.asset_bars(options)
        click.echo(click.style("\nFAILED", fg="red") +" with status code 422:")
        click.echo("Due to licensing restrictions, you can only access US equity data from Tradologics servers (tradelets, research, etc)")


# asset router function
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('options', nargs=-1, type=click.UNPROCESSED,
                callback=exchanges_options_validator)
def exchanges(options):
    """Access exchange and calendar information"""
    command, options = options

    if command in ["ls", "list"]:
        exchanges_crud.exchanges_list(options)

    if command in ["info"]:
        exchanges_crud.exchange_info(options)

    if command in ["calendar"]:
        exchanges_crud.exchange_calendar(options)
