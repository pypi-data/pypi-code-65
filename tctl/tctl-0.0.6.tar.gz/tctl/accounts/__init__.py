#!/usr/bin/env python

import click
import sys
from .. import utils
from . import crud


COMMANDS = {
    "ls": "    Retreive accounts list",
    "list": "  Retreive accounts list",
    "info": "  Show account information (via --account|-a <ACCOUNT-ID>)",
    "new": "   Create new account",
    "update": "Update existing account (via --account|-a <ACCOUNT-ID>)",
    "delete": "Delete account (via --account|-a <ACCOUNT-ID>)",
    "rm": "    Delete account (via --account|-a <ACCOUNT-ID>)"
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
            "account": ["-a", "--account"],
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
def accounts(options):
    """List, create, update, or delete broker accounts"""
    command, options = options
    # print(command, options)

    if command in ["ls", "list"]:
        crud.accounts_list(options)

    elif command == "info":
        crud.account_info(options)

    elif command == "new":
        crud.account_create(options)

    elif command == "update":
        crud.account_update(options)

    elif command in ["rm", "delete"]:
        crud.account_delete(options)

