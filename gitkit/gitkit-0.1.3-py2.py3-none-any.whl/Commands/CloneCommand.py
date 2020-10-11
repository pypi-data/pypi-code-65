# pylint: disable=no-self-argument
from click.decorators import pass_context
from gitkit.Models.CommandContext import CommandContext
from gitkit.Models.Commands import Commands
from typing import List
import click


class CloneCommand:

   @click.group(name='clone', invoke_without_command=True, help="Clone repositories")
   @click.option('-p/-np', '--pull/--no-pull', is_flag=True, default=True, help='Pull existent repositories')
   @click.option('--group', multiple=True, type=click.Choice(['fork', 'owner', 'project'], case_sensitive=False))
   def clone(pull: bool, group: List[str]):
      ctx = click.get_current_context()
      context = ctx.obj["CommandContext"]
      executer = ctx.obj["CommandExecuter"]

      context.commands.append(Commands.clone)
      context.pullExistingWhileClone = pull
      context.cloneGroups = group
      executer.TryExecute(context)

   # @clone.command(name='filter', help='Filter repositories befor cloning')
   # @click.option('-p/-np', '--private/--no-private', is_flag=True, default=None, help='Default with private and public. -p = Private only. -np = Public only')
   # @click.option('-f/-nf', '--forks/--no-forks', is_flag=True, default=None, help='Default with forks. -f = Forks only. -nf = Without forks')
   # @click.option('-o/-no', '--owner/--no-owner', is_flag=True, default=None, help='Default owned and not owned. -o = Owned only. -no = Not owned only.')
   # @click.option('-d/-nd', '--dirty/--no-dirty', is_flag=True, default=None, help='Default clean and dirty. -d = Dirty only. -nd = Clean only')
   # def filter(forks: bool, private: bool, owner: bool, dirty: bool):
   #    ctx = click.get_current_context()
   #    context = ctx.obj["CommandContext"]
   #    executer = ctx.obj["CommandExecuter"]

   #    context.setFilter(
   #        forks, private, owner, dirty
   #    )
   #    executer.TryExecute(context)
