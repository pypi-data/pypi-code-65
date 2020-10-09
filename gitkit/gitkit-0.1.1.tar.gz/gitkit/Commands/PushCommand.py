# pylint: disable=no-self-argument
from gitkit.Models.Commands import Commands
import click


class PushCommand:

   @click.group(name='push', invoke_without_command=True, help="Push repositories")
   @click.option('-a/-na', '--add/--no-add', is_flag=True, default=False, help='Add before push')
   @click.option('-c/-nc', '--commit/--no-commit', is_flag=True, default=False, help='Commit before push')
   def push(add: bool, commit: bool):
      ctx = click.get_current_context()
      context = ctx.obj["CommandContext"]
      executer = ctx.obj["CommandExecuter"]

      context.commands.append(Commands.push)
      context.addUnstaged = add
      context.commitBeforePush = commit
      executer.TryExecute(context)

      click.echo(f'push: add:{add}, commit: {commit}')

   # @push.command(name='filter', help='Filter repositories befor pushing')
   # @click.option('-p/-np', '--private/--no-private', is_flag=True, default=None, help='Default with private and public. -p = Private only. -np = Public only')
   # @click.option('-f/-nf', '--forks/--no-forks', is_flag=True, default=None, help='Default with forks. -f = Forks only. -nf = Without forks')
   # @click.option('-o/-no', '--owner/--no-owner', is_flag=True, default=None, help='Default owned and not owned. -o = Owned only. -no = Not owned only.')
   # @click.option('-d/-nd', '--dirty/--no-dirty', is_flag=True, default=None, help='Default clean and dirty. -d = Dirty only. -nd = Clean only')
   # def filter(forks: bool, private: bool, owner: bool, dirty: bool):
   #    ctx = click.get_current_context()
   #    context = ctx.obj["CommandContext"]
   #    executer = ctx.obj["CommandExecuter"]

   #    context.setFilter(
   #        forks, private,  owner, dirty
   #    )
   #    executer.TryExecute(context)
