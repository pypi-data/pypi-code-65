# pylint: disable=no-self-argument
# pylint: disable=no-method-argument
import click
from gitkit.Models.Commands import Commands


class PullCommand:

   @click.group(name='pull', invoke_without_command=True, help="pull repositories")
   def pull():
      ctx = click.get_current_context()
      context = ctx.obj["CommandContext"]
      executer = ctx.obj["CommandExecuter"]

      context.commands.append(Commands.pull)
      executer.TryExecute(context)

   # @pull.command(name='filter', help='Filter repositories befor commiting')
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
