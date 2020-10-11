# pylint: disable=too-many-function-args
from ast import Str
from gitkit.LogProvider import LogProvider
from gitkit.GitRepository import GitRepository
from gitkit.GitRepositoryFactory import GitRepositoryFactory
import os
from typing import Any, List, cast, overload

import git
from git import Repo
from git.exc import InvalidGitRepositoryError
from github import Github
from github.AuthenticatedUser import AuthenticatedUser
from github.Repository import Repository

from gitkit.GithubRepositoryType import GithubRepositoryType

logger = LogProvider().getLogger(__name__)

class GithubRepositoryService:

   @property
   def LoginName(self) -> str:
      return self._user.login

   def __init__(self, username: str, password: str, preload: bool = False) -> None:
      g = Github(username, password)
      self._user = cast(AuthenticatedUser, g.get_user())

      if preload:
         self.preloadedRepos = self.__preloadRemoteRepos()
      else:
         self.preloadedRepos = None

   def LoadRepos(self, localRepos: List[Repo]) -> List[GitRepository]:
      localNames = list(map(self.__extractRepoName, localRepos))
      remoteRepos = self.preloadedRepos or self.__preloadRemoteRepos()
      requestedRemoteRepos = list(
          filter(lambda item: item.name in localNames, remoteRepos))

      pairs = GitRepositoryFactory.createList(localRepos, requestedRemoteRepos)
      return pairs

   def __preloadRemoteRepos(self, preloadChilds: bool = False) -> List[Repository]:
      remoteRepos = list(self._user.get_repos())

      if preloadChilds:
         for repo in remoteRepos:
            repo.owner.name   # Preload child object

      return remoteRepos
         

   def GetForkedRepos(self) -> List[Repo]:
      return self.GetRepos(includeForks=True)

   def GetOwnedRepos(self) -> List[Repo]:
      return self.GetRepos(repoType=GithubRepositoryType.owner)

   def GetRepos(self, repoType: GithubRepositoryType = GithubRepositoryType.all, includeForks=True) -> List[Repo]:
      allRepos = self.preloadedRepos or list(self._user.get_repos())

      allRepos = list(filter(lambda r: True, allRepos))

      if not includeForks:
         allRepos = list(filter(lambda r: not r.fork, allRepos))

      if repoType == GithubRepositoryType.owner:
         userName = self._user.name
         allRepos = list(filter(lambda r: r.owner.name == userName, allRepos))

      if repoType == GithubRepositoryType.private:
         allRepos = list(filter(lambda r: r.private, allRepos))

      if repoType == GithubRepositoryType.public:
         allRepos = list(filter(lambda r: not r.private, allRepos))

      return list(allRepos)

   def CloneRepo(self, repoName: str, repoPath: str):

      remoteRepo = self._user.get_repo(repoName)
      Repo.clone_from(remoteRepo.clone_url, repoPath)

   def CloneOrPullRepo(self, repoName: str, repoPath: str):

      if os.path.exists(repoPath):
         localRepo = Repo(repoPath)
         localRepo.remotes.origin.pull()
      else:
         remoteRepo = self._user.get_repo(repoName)
         for item in list(remoteRepo.get_projects()):
            print(item.name)

         Repo.clone_from(remoteRepo.clone_url, repoPath)

   def CloneOrPullForks(self, targetPath: str):
      # https://developer.github.com/v3/repos/#parameters
      allRepos = self.preloadedRepos or list(self._user.get_repos())
      allRepos = list(filter(lambda r: r.fork, allRepos))

      for repo in allRepos:

         try:

            print(
                f'Repo: {repo.name} | Fork: {repo.fork} | Path: {targetPath}')

            repoPath = f'{targetPath}/{repo.name}'

            if os.path.exists(repoPath):
               # Pull local existing repo
               localRepo = Repo(repoPath)
               localRepo.remotes.origin.pull()
            else:
               # Clone
               Repo.clone_from(repo.clone_url, repoPath)

         except Exception as e:
            print(e)

   @overload
   def FindDirtyRepos(self, path: str, untracked_files=True) -> List[Repo]:
      ...

   @overload
   def FindDirtyRepos(self, path: List[str], untracked_files=True) -> List[Repo]:
      ...

   @overload
   def FindDirtyRepos(self, path: List[Repo], untracked_files=True) -> List[Repo]:
      ...

   def FindDirtyRepos(self, path, untracked_files=True) -> List[Repo]:
      repos = self.__toRepoList(path)

      return list(filter(lambda r: r.is_dirty(index=True, untracked_files=untracked_files), repos))

   def isListof(self, obj: any, itemType: type) -> bool:
      if isinstance(obj, List):
         return any(isinstance(item, itemType) for item in obj)
      else:
         return False

   @overload
   def FindLocalRepos(self, path: str) -> List[Repo]:
      ...

   def FindLocalRepos(self, path: List[str]) -> List[Repo]:
      # List of Repos found
      result = []
      # Directories to test
      repoDirs = []

      if self.isListof(path, str):
         repoDirs = path
      else:
         repoDirs = [path]

      dirs = []
      for dir in repoDirs:
         dirs += [f for f in os.scandir(dir) if f.is_dir()]

      for dir in dirs:

         try:
            localRepo = Repo(dir.path)
            result.append(localRepo)

         except InvalidGitRepositoryError:
            # No repository, lookup sub dirs
            logger.info(f'Root folder {dir.path} found')
            subRepos = self.FindLocalRepos(dir.path)
            result += subRepos

      return result

   @overload
   def Commit(self, rootPath: str, push: bool = True):
      ...

   @overload
   def Commit(self, rootPaths: List[str], push: bool = True):
      ...

   @overload
   def Commit(self, repo: Repo, push: bool = True):
      ...

   def Commit(self, repoList: Any, push: bool = True):
      repos = self.__toRepoList(repoList)

      pc = os.uname().nodename

      for repo in repos:
         author = repo.config_reader().get_value("user", "email")
         # TODO: Activate
         repo.git.commit('-m', f'DotupGitKit {pc}', author=author)

         if push:
            self.Push(repo)

   @overload
   def Push(self, rootPath: str):
      ...

   @overload
   def Push(self, repo: Repo):
      ...

   @overload
   def Push(self, repoList: Any):

      repos = self.__toRepoList(repoList)

      for repo in repos:
         repo.remotes.origin.push()

   def __toRepoList(self, source: Any) -> List[Repo]:

      repos = []

      if self.isListof(source, Repo):
         # Already a list of Repo
         repos = source
      elif self.isListof(source, str):
         # Already a list of Repo
         repos = self.FindLocalRepos(source)
      elif isinstance(source, str):
         # A single directory
         repos = self.FindLocalRepos(source)
      else:
         # Just a single repo
         repos = [source]

      return repos

   def __extractRepoName(self, repo: Repo) -> str:
      if repo.remotes.origin == None:
         return ""

      urls = list(repo.remotes.origin.urls)
      remote = str(urls[0])
      return remote.split("/")[-1].replace(".git", "")
