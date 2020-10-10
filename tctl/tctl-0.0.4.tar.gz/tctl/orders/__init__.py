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

    optional = {}
    required = {}

    if command in ["info", "update", "delete", "rm"]:
        required = {
            "order": ["-o", "--order"],
        }

    elif command == "new":
        optional = {
            "type": ["-t", "--type"],
        }

    elif command in ["ls", "list"]:
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
def orders(options):
    command, options = options

    if command in ["ls", "list"]:
        crud.orders_list(options)

    elif command == "info":
        crud.order_info(options)

    elif command == "new":
        crud.order_create(options)

    elif command == "update":
        crud.order_update(options)

    elif command in ["rm", "delete"]:
        crud.order_delete(options)

