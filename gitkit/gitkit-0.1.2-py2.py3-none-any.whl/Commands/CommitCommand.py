# pylint: disable=no-self-argument
from gitkit.Models.Commands import Commands
import click

# Command Group


class CommitCommand:

   @click.group(name='commit', invoke_without_command=True, help="Commit repositories")
   @click.option('-a/-na', '--add/--no-add', is_flag=True, default=True, help='Add unstaged files')
   @click.option('-p/-np', '--push/--no-push', is_flag=True, default=True, help='Push after commit')
   def commit(add: bool, push: bool):
      ctx = click.get_current_context()
      context = ctx.obj["CommandContext"]
      executer = ctx.obj["CommandExecuter"]

      context.commands.append(Commands.commit)
      context.addUnstaged = add
      context.pushAfterCommit = push
      executer.TryExecute(context)

   # @commit.command(name='filter', help='Filter repositories befor commiting')
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
