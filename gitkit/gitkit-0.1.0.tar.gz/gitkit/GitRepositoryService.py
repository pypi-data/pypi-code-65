import logging
import os
from typing import Any, List, overload

from git import Repo
from git.exc import InvalidGitRepositoryError


class GitRepositoryService:

   def __init__(self):
      pass

   def GetRepos(self, path: str) -> List[Repo]:
      allRepos = self.FindLocalRepos(path)

      return allRepos

   def GetDirtyRepos(self, path: str) -> List[Repo]:
      allRepos = self.FindLocalRepos(path)
      allRepos = filter(lambda r: r.is_dirty(untracked_files=True), allRepos)
      return allRepos

   def GetCleanRepos(self, path: str) -> List[Repo]:
      allRepos = self.FindLocalRepos(path)
      allRepos = filter(lambda r: not r.is_dirty(untracked_files=True), allRepos)
      return allRepos

   def CloneOrPullRepo(self, repoName: str, repoPath: str, clone_url: str):

      if os.path.exists(repoPath):
         localRepo = Repo(repoPath)
         localRepo.remotes.origin.pull()
      else:
         Repo.clone_from(clone_url, repoPath)

   @overload
   def FindDirtyRepos(self, path: str, untracked_files=True) -> List[Repo]:
      ...

   @overload
   def FindDirtyRepos(self, path: List[str], untracked_files=True) -> List[Repo]:
      ...

   def FindDirtyRepos(self, path, untracked_files=True) -> List[Repo]:
      if self.isListof(path, str):
         repos = self.FindLocalRepos(path)
      elif self.isListof(path, Repo):
         repos = path
      else:
         repos = self.FindLocalRepos(path)

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

         except InvalidGitRepositoryError as e:
            # No repository, lookup sub dirs
            logging.info(f'Analysing subfolders: {dir.path}')
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
      repos = []

      if self.isListof(repoList, Repo):
         # Already a list of Repo
         repos = repoList
      elif self.isListof(repoList, str):
         # Already a list of Repo
         repos = self.FindLocalRepos(repoList)
      elif isinstance(repoList, str):
         # A single directory
         repos = self.FindLocalRepos(repoList)
      else:
         # Just a single repo
         repos = [repoList]

      pc = os.uname().nodename

      for repo in repos:
         author = repo.config_reader().get_value("user", "email")
         repo.git.commit('-m', f'DotupGitKit {pc}', author=author)

         # TODO: Activate
         # if push:
         #    self.Push(repo)

   @staticmethod
   def GetRepoName(repo: Repo) -> str:
      if repo.remotes.origin == None:
         return ""

      urls = list(repo.remotes.origin.urls)
      remote = str(urls[0])
      return remote.split("/")[-1].replace(".git", "")
