#!/usr/bin/env python

import click
import sys
from .. import utils
from . import crud


COMMANDS = {
    "ls": "    Retreive monitors list",
    "list": "  Retreive monitors list",
    "new": "   Create new monitor",
    "delete": "Delete monitor (via --monitor|-m <MONITOR-ID>)",
    "rm": "    Delete monitor (via --monitor|-m <MONITOR-ID>)",
}


def options_validator(ctx, param, args):
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
    if command in ["info", "update", "delete", "rm"]:
        required = {
            "monitor": ["-m", "--monitor"],
        }
    elif command in ["ls", "new"]:
        required = {
            "strategy": ["-s", "--strategy"]
        }
    elif command == "new":
        optional = {
            "type": ["-t", "--type"],
        }

    args = utils.args_parser(args, required, optional, flags)

    return command, args


@click.group()
def cli():
    pass


# router function
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('options', nargs=-1, type=click.UNPROCESSED,
                callback=options_validator)
def monitors(options):
    """List, create, update, or delete monitors"""
    command, options = options
    # print(command, options)

    if command in ["ls", "list"]:
        crud.monitors_list(options)

    elif command == "new":
        crud.monitor_create(options)

    elif command in ["rm", "delete"]:
        crud.monitor_delete(options)

