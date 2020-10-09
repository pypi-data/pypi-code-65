from gitkit.GitRepositoryService import GitRepositoryService
from typing import List

from git.repo.base import Repo
from github.Repository import Repository
from gitkit.GitRepository import GitRepository


class GitRepositoryFactory:
   @staticmethod
   def createList(local: List[Repo], remote: List[Repository]) -> List[GitRepository]:
      """
      docstring
      """
      result: List[GitRepository] = []

      for l in local:
         repoName = GitRepositoryService.GetRepoName(l)
         pair = GitRepository(repoName)
         pair.SetLocal(l)
         pair.SetRemote(next((r for r in remote if r.name == repoName), None))
         result.append(pair)

      notLocal = list(filter(lambda r: not any(item.Remote == r for item in result), remote))

      for r in notLocal:
         pair = GitRepository(r.name)
         pair.SetLocal(None)
         pair.SetRemote(r)
         result.append(pair)

      return result
