#!/usr/bin/env python

import click
import sys
from .. import utils
from . import crud


COMMANDS = {
    "ls": "    Retreive orders list",
    "list": "  Retreive orders list",
    "info": "  Show order information (via --order|-o <ORDER-ID>)",
    "new": "   Create new order",
    "update": "Update existing order (via --order|-o <ORDER-ID>)",
    "delete": "Delete (cancel) order (via --order|-o <ORDER-ID>)",
    "rm": "    Delete (cancel) order (via --order|-o <ORDER-ID>)",
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
    """List, create, update, or cancel orders"""
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

