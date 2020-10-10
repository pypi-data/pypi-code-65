#!/usr/bin/env python

import click
import sys
from .. import utils
from . import crud


COMMANDS = {
    "ls": "    Retreive Tradehooks list",
    "list": "  Retreive Tradehooks list",
    "info": "  Show Tradehook information (via --tradehook|-t <TRADEHOOK-ID>)",
    "new": "   Create new Tradehook",
    "update": "Update existing Tradehook (via --tradehook|-t <TRADEHOOK-ID>)",
    "delete": "Delete Tradehook (via --tradehook|-t <TRADEHOOK-ID>)",
    "rm": "    Delete Tradehook (via --tradehook|-t <TRADEHOOK-ID>)",
    "attach": "Attach Tradehook to strategy (via --tradehook|-t <TRADEHOOK-ID>, optional: --strategy <STRATEGY-ID>)"
}


def options_validator(ctx, param, args):
    cmd = [f"{k}  {v}" for k, v in COMMANDS.items()]
    if len(args) == 0:
        click.echo("Usage: tctl {command} ACTION [OPTIONS]...".format(command=sys.argv[1]))
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
    if command in ["info", "update", "delete", "rm", "attach"]:
        required = {
            "tradehook": ["-t", "--tradehook"],
        }
        if command == "attach":
            optional = {
                "strategy": ["-s", "--strategy"]
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
def tradehooks(options):
    """List, create, update, or delete Tradehooks"""
    command, options = options
    # print(command, options)

    if command in ["ls", "list"]:
        crud.tradehooks_list(options)

    elif command == "info":
        crud.tradehook_info(options)

    elif command == "new":
        crud.tradehook_create(options)

    elif command == "update":
        crud.tradehook_update(options)

    if command in ["rm", "delete"]:
        crud.tradehook_delete(options)

    elif command == "attach":
        crud.tradehook_attach(options)

