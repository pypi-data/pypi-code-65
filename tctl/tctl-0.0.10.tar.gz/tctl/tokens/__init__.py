#!/usr/bin/env python

import click
import sys
from .. import utils
from . import crud


COMMANDS = {
    "ls": "      Retreive list of active tokens (optional: --full)",
    "list": "    Retreive list of active tokens (optional: --full)",
    "info": "    Show tokens (via --token|-t <TOKEN-ID>)",
    "new": "     Create new token",
    "extend": "  Update token's expiry (via ---token|-t <TOKEN-ID>, optional: --ttl <SECONDS>)",
    "delete": "  Delete tokens (via ---token|-t <TOKEN-ID>)",
    "rm": "      Delete tokens (via ---token|-t <TOKEN-ID>)",
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
    if command in ["info", "extend", "delete", "rm"]:
        required = {
            "token": ["-t", "--token"],
        }
    if command in ["info", "ls", "list"]:
        flags = {
            "full": ["--full"],
        }

    if command in ["extend"]:
        optional = {
            "ttl": ["--ttl"],
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
def tokens(options):
    """List, create, extend, or delete tokens"""
    command, options = options
    # print(command, options)

    if command in ["ls", "list"]:
        crud.tokens_list(options)

    elif command == "info":
        crud.token_info(options)

    elif command == "new":
        crud.token_create(options)

    elif command == "extend":
        crud.token_extend(options)

    elif command in ["rm", "delete"]:
        crud.token_delete(options)

