#!/usr/bin/env python

import click
from .. import utils
from . import crud


COMMANDS = ["ls", "list", "info", "new", "update", "delete", "rm", "attach"]


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

