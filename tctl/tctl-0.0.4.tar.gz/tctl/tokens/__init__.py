#!/usr/bin/env python

import click
from .. import utils
from . import crud


COMMANDS = ["ls", "list", "info", "new", "extend", "delete", "rm"]


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
    if command in ["info", "extend", "delete", "rm"]:
        required = {
            "token": ["-t", "--token"],
        }
    if command in ["info", "ls", "list"]:
        flags = {
            "full": ["--full"],
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

