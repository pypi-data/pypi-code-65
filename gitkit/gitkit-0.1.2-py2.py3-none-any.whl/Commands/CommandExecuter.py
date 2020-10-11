import os
from typing import List

import click
from gitkit.GithubRepositoryService import GithubRepositoryService
from gitkit.GitRepository import GitRepository
from gitkit.GitRepositoryFactory import GitRepositoryFactory
# from gitkit.Commands.CommandContext import COMMAND_CONTEXT, Commands
from gitkit.GitRepositoryService import GitRepositoryService
from gitkit.LogProvider import LogProvider
from gitkit.Models.CommandContext import CommandContext
from gitkit.Models.Commands import Commands

logger = LogProvider().getLogger(__name__)


class CommandExecuter:

   __service: GithubRepositoryService = None

   def TryExecute(self, context: CommandContext) -> bool:
      ctx = click.get_current_context()
      if ctx.invoked_subcommand is None:
         self.Execute(context)
         return True
      else:
         return False

   def Execute(self, context: CommandContext):
      repositories = self.__filter(context)

      for command in context.commands:

         if command == Commands.find:

            if context.filters.listOnly:
               for r in repositories:
                  print(f'{r}')

         elif command == Commands.clone:
            self.__executeClone(repositories, context)
            pass

         elif command == Commands.commit:
            self.__executeCommit(repositories, context)

         elif command == Commands.pull:
            self.__executePull(repositories, context)

         elif command == Commands.push:
            self.__executePush(repositories, context)

   def __filter(self, context: CommandContext) -> List[GitRepository]:
      f = context.filters
      logger.debug(f'filter: forks:{f.forks}, private: {f.private}, owner: {f.owner}, dirty: {f.dirty}, behind: {f.behind}, ahead: {f.ahead}')

      git = GitRepositoryService()

      # Load local repositories
      # if context.filters.dirty == True:
      #    repos = list(git.GetDirtyRepos(context.localDir))
      # elif context.filters.dirty == False:
      #    repos = list(git.GetCleanRepos(context.localDir))
      # else:
      repos = list(git.GetRepos(context.localDir))

      # Load github data
      if context.isGithubRequired():
         self.__service = GithubRepositoryService(context.user, context.password)
         remotes = self.__service.GetRepos()
      else:
         remotes = []

      repositories = GitRepositoryFactory.createList(repos, remotes)

      # dirty filter
      if context.filters.dirty == True:
         repositories = GitRepository.GetDirty(repositories)
      elif context.filters.dirty == False:
         repositories = GitRepository.GetClean(repositories)

      # forks filter
      if context.filters.forks == True:
         repositories = GitRepository.GetForked(repositories)
      elif context.filters.forks == False:
         repositories = GitRepository.GetNotForked(repositories)

      # owner filter
      if context.filters.owner == True:
         repositories = GitRepository.GetOwned(repositories, self.__service.LoginName)
      elif context.filters.owner == False:
         repositories = GitRepository.GetNotOwned(repositories, self.__service.LoginName)

      # Private filter
      if context.filters.private == True:
         repositories = GitRepository.GetPrivate(repositories)
      elif context.filters.private == False:
         repositories = GitRepository.GetPublic(repositories)

      # ahead filter
      if context.filters.ahead == True:
         repositories = GitRepository.GetAheadRemote(repositories)
      elif context.filters.ahead == False:
         repositories = GitRepository.GetNotAheadRemote(repositories)

      # behind filter
      if context.filters.behind == True:
         repositories = GitRepository.GetBehindRemote(repositories)
      elif context.filters.behind == False:
         repositories = GitRepository.GetNotBehindRemote(repositories)

      return repositories

   def __executePull(self, repositories: List[GitRepository], context: CommandContext):
      for repo in repositories:

         if repo.Local == None:
            logger.warning(f'No local repository for {repo}')
            continue

         # pull each remote
         for r in repo.Local.remotes:
            try:
               if not context.filters.listOnly:
                  r.pull()
               logger.info(f'{repo.Local.working_dir} pulled from "{r.name}"')
            except Exception as e:
               logger.exception(f'Pull failed: {repo.Local.working_dir}', e)

   def __executeCommit(self, repositories: List[GitRepository], context: CommandContext):
      for repo in repositories:

         if repo.Local == None:
            logger.warning(f'No local repository for {repo}')
            continue

         if context.filters.listOnly:
            print(f'commiting: {repo.Local.working_dir}')
            continue

         try:
            repo.Commit(context.addUnstaged)

            if context.pushAfterCommit:
               repo.Push()

            logger.info(f'commited: {repo.Local.working_dir}')
         except Exception as e:
            logger.exception(f'Commit failed: {repo.Local.working_dir}', e)

   def __executePush(self, repositories: List[GitRepository], context: CommandContext):
      for repo in repositories:

         if repo.Local == None:
            logger.warning(f'No local repository for {repo}')
            continue

         # if repo.Remote == None:
         #    logger.warning(f'No remote repository for {repo}')
         #    continue

         if not repo.GetPushRequired():
            logger.debug(f'No push required on {repo.Local.working_dir}')
            continue

         if context.filters.listOnly:
            print(f'{repo.Local.working_dir} pushed')
         else:
            repo.Push()

         # pull each remote
         # for r in repo.Local.remotes:
         #    try:
         #       if not context.filters.listOnly:
         #          r.push()
         #       logger.info(f'{repo.Local.working_dir} pushed to "{r.name}"')
         #    except Exception as e:
         #       logger.exception(f'Push failed: {repo.Local.working_dir}', e)
   
   def __executeClone(self, repositories: List[GitRepository], context: CommandContext):

      # clone group Choice(['project', 'fork', 'owner']
      for repo in repositories:

         targetPath = context.localDir

         if 'owner' in context.cloneGroups:
            targetPath = os.path.join(targetPath, repo.Remote.owner.login)

         if 'fork' in context.cloneGroups:
            if repo.forked:
               targetPath = os.path.join(targetPath, 'forks')

         if 'project' in context.cloneGroups:
            p = repo.GetProjectName() # .Remote.get_projects()[-1]
            targetPath = os.path.join(targetPath, p)

         targetPath = os.path.join(targetPath, repo.Name)

         if context.filters.listOnly:
            print(f'Clone {repo.Name} to {targetPath}')
         else:            
            self.__service.CloneRepo(repo.Name, targetPath)
