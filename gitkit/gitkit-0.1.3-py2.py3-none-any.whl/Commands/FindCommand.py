# pylint: disable=no-self-argument
# pylint: disable=no-method-argument
from typing import List
from gitkit.Models.Commands import Commands
import click


class FindCommand:

   # gitkit find --forks --private --dirty
   @click.group(name='find', invoke_without_command=True, help="Search local repositories")
   @click.option('-p/-np', '--private/--no-private', is_flag=True, default=None, help='Default with private and public. -p = Private only. -np = Public only')
   @click.option('-f/-nf', '--forks/--no-forks', is_flag=True, default=None, help='Default with forks. -f = Forks only. -nf = Without forks')
   @click.option('-o/-no', '--owner/--no-owner', is_flag=True, default=None, help='Default owned and not owned. -o = Owned only. -no = Not owned only.')
   @click.option('-d/-nd', '--dirty/--no-dirty', is_flag=True, default=None, help='Default clean and dirty. -d = Dirty only. -nd = Clean only')
   @click.option('-a/-na', '--ahead/--no-ahead', is_flag=True, default=None, help='-a = local branch is ahead of remote. -nd = local branch is not ahead of remote')
   @click.option('-b/-nb', '--behind/--no-behind', is_flag=True, default=None, help='-b = local branch is behind remote. -nd = local branch is not behind remote')
   @click.option('-r', '--remote', is_flag=True, default=None, help='-r = Remote github repositories only.')
   def find(forks: bool, private: bool, owner: bool, dirty: bool, ahead: bool, behind: bool, remote: bool):
      ctx = click.get_current_context()
      context = ctx.obj["CommandContext"]
      executer = ctx.obj["CommandExecuter"]
      context.commands.append(Commands.find)
      context.setFilter(
          forks, private, owner, dirty, ahead, behind, remote
      )
      executer.TryExecute(context)

   @find.command(name='push', help='Push repositories to remotes')
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

   @find.command(name='pull', help='Pull repositories from remotes')
   def pull():
      ctx = click.get_current_context()
      context = ctx.obj["CommandContext"]
      executer = ctx.obj["CommandExecuter"]

      context.commands.append(Commands.pull)
      executer.TryExecute(context)

   @find.command(name='commit', help='Commit repositories')
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

   @find.command(name='clone', help='Clone repositories')
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
