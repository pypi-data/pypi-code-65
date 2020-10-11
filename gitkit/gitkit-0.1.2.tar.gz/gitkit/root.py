from gitkit.LogProvider import LogProvider
import logging
from gitkit.Commands.CommandExecuter import CommandExecuter
import os
from os import environ

import click

from gitkit.Commands.CloneCommand import CloneCommand
from gitkit.Commands.CommitCommand import CommitCommand
from gitkit.Commands.FindCommand import FindCommand
from gitkit.Commands.PullCommand import PullCommand
from gitkit.Commands.PushCommand import PushCommand
from gitkit.Models.CommandContext import CommandContext

# gitkit push --add --commit --message="GI" filter --forks --private

# gitkit find --forks --private --dirty

# gitkit -u dotupNET -p secret find --forks pull --all


logger = LogProvider().getLogger(__name__)
logger2 = LogProvider().getLogger("f")

@click.group()
@click.option('-t', '--target-dir', type=str, default=None, help="The local target path")
@click.option('-u', '--user', type=str, help="The github username")
@click.option('-p', '--password', type=str, help="The github password")
@click.option('-l', '--list', is_flag=True, default=False, help='Print only results. Does not execute any command.')
def cli(target_dir: str, user: str, password: str, list:  bool):
   """Gitkit - A powerful git and github tool"""
   commandContext = CommandContext()

   commandContext.localDir = target_dir if target_dir != None else environ.get("targetdir") or os.getcwd()
   commandContext.user = user if user != None else environ.get("user")
   commandContext.password = password if password != None else environ.get("password")

   commandContext.filters.listOnly = list if list != None else environ.get("list")
   ctx = click.get_current_context()

   obj = {}
   obj["CommandContext"] = commandContext
   obj["CommandExecuter"] = CommandExecuter()
   ctx.obj = obj


cli.add_command(CloneCommand().clone)
cli.add_command(CommitCommand().commit)
cli.add_command(FindCommand().find)
cli.add_command(PullCommand().pull)
cli.add_command(PushCommand().push)

if environ.get("DEBUG") != None:
   logger.info("main")
   # cli.add_command(CloneCommand().clone)
   # cli.add_command(CommitCommand().commit)
   # cli.add_command(FindCommand().find)
   # cli.add_command(PullCommand().pull)
   # cli.add_command(PushCommand().push)
   # None will be overriden by Click...
   cli(None, None, None, None)
