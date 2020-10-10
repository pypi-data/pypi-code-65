#!/usr/bin/env python

import click
from .. import utils
from . import crud


COMMANDS = ["ls", "list", "info", "new", "update", "delete", "rm"]


def options_validator(ctx, param, args):
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

