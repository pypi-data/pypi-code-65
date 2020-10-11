from gitkit.LogProvider import LogProvider
from typing import Any, List

from git.repo.base import Repo
from github.NamedUser import NamedUser
from github.Repository import Repository

from gitkit.GitRepositoryState import GitRepositoryState

logger = LogProvider().getLogger(__name__)

class GitRepository:
   """
   Remote and local repository
   """

   def __init__(self, name: str) -> None:
      self.__name = name
      self.__local = None
      self.__remote = None
      self.__location = GitRepositoryState.Unknown

   @property
   def Name(self) -> str:
      return self.__name

   @property
   def Local(self) -> Repo:
      return self.__local

   @property
   def Remote(self) -> Repository:
      return self.__remote

   @property
   def Location(self) -> GitRepositoryState:
      return self.__location

   @property
   def forked(self) -> bool:
      if self.Remote == None:
         return False
      else:
         return self.Remote.fork

   def GetIsDirty(self, untracked_files: bool = True) -> bool:
      if self.Local == None:
         return False
      else:
         return self.Local.is_dirty(untracked_files=untracked_files)

   def GetPushRequired(self)-> bool:
      # u = "{u}"
      for branch in self.Local.branches:
         # TODO: Use remotes instead of fixed origin
         # x = list(self.Local.iter_commits(f'{branch.name}..origin/{branch.name}'))
         # ic = list(self.Local.iter_commits(f'{branch.name}..{branch.name}@{u}'))
         # mic = list(self.Local.iter_commits(f'{branch.name}@{u}..{branch.name}'))

         # if len(ic) > 0 or len(mic) > 0:
         # if len(x) > 0:
         if self.GetIsAheadRemote():
            return True
         else:
            continue

   ### commits ahead = repo.iter_commits('origin/master..master')
   def GetIsAheadRemote(self)-> bool:
      for branch in self.Local.branches:
         # TODO: Use remotes instead of fixed origin
         x = list(self.Local.iter_commits(f'origin/{branch.name}..{branch.name}'))

         if len(x) > 0:
            return True
         else:
            continue

   ### commits behind = repo.iter_commits('master..origin/master')
   def GetIsBehindRemote(self)-> bool:
      for branch in self.Local.branches:
         # TODO: Use remotes instead of fixed origin
         x = list(self.Local.iter_commits(f'{branch.name}..origin/{branch.name}'))

         if len(x) > 0:
            return True
         else:
            continue

   def GetIsOwn(self, loginName: str) -> bool:
      if self.Remote == None:
         return False
      else:
         return self.Remote.owner.login == loginName

   def GetIsPrivate(self) -> bool:
      if self.Remote == None:
         return False
      else:
         return self.Remote.private

   def GetProjectName(self) -> str:
      if self.Remote == None:
         return ""

      projects = list(self.Remote.get_projects(state='open'))

      if len(projects) > 0:
         return projects[0]
      else:
         return ""

   @staticmethod
   def GetDirty(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: r.GetIsDirty(True), items))

   @staticmethod
   def GetClean(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: not r.GetIsDirty(True), items))

   @staticmethod
   def GetForked(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: r.forked, items))

   @staticmethod
   def GetNotForked(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: not r.forked, items))

   @staticmethod
   def GetOwned(items: List["GitRepository"], owner: NamedUser) -> List["GitRepository"]:
      return list(filter(lambda r: r.GetIsOwn(owner), items))

   @staticmethod
   def GetNotOwned(items: List["GitRepository"], owner: NamedUser) -> List["GitRepository"]:
      return list(filter(lambda r: not r.GetIsOwn(owner), items))

   @staticmethod
   def GetPrivate(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: r.GetIsPrivate(), items))

   @staticmethod
   def GetPublic(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: not r.GetIsPrivate(), items))

   @staticmethod
   def GetAheadRemote(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: r.GetIsAheadRemote(), items))

   @staticmethod
   def GetNotAheadRemote(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: not r.GetIsAheadRemote(), items))

   @staticmethod
   def GetBehindRemote(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: r.GetIsBehindRemote(), items))

   @staticmethod
   def GetNotBehindRemote(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: not r.GetIsBehindRemote(), items))

   @staticmethod
   def GetRemoteOnly(items: List["GitRepository"]) -> List["GitRepository"]:
      return list(filter(lambda r: r.Local == None, items))

   def SetLocal(self, local: Repo) -> None:
      self.__local = local
      if local != None:
         #    self._state &= ~GitRepositoryState.Local
         # else:
         self.__location |= GitRepositoryState.Local
         if self.Local.remotes.origin != None:
            self.__location |= GitRepositoryState.Remote

   def SetRemote(self, remote: Repository) -> None:
      self.__remote = remote
      if remote != None:
         #    self._state &= ~GitRepositoryState.Remote
         # else:
         self.__location |= GitRepositoryState.Remote

   @staticmethod
   def Diff(list1, list2) -> List[Any]:
      left = list1
      right = list2
      listDiff = [i for i in left if i not in right]
      return listDiff

   def __str__(self) -> str:
      url = ""

      if self.Local == None:
         localDir = "--- "
         state = "---"
      else:
         localDir = self.Local.working_dir
         if self.Local.remotes != None:
            url = list(self.Local.remotes.origin.urls)[0]
         state = "dirty" if self.GetIsDirty() else "clean"

      if self.Remote != None:
         url = self.Remote.clone_url

      return f'{self.Location} [{state}], {self.Name}, {localDir}, {url}'

   def Push(self)-> None:
      for r in self.Local.remotes:
         try:
            r.push()
            logger.info(f'{self.Local.working_dir} pushed to "{r.name}"')
         except Exception as e:
            logger.exception(f'Push failed: {self.Local.working_dir}', e)

   def Commit(self, addFiles: bool = True)-> None:
      if addFiles:
         self.Local.git.add(update=True)

      self.Local.commit()
