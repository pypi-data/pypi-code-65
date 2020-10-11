from enum import Enum
from gitkit.Models.Commands import Commands
from gitkit.Models.Filters import Filters
from typing import List

class CommandContext:

   user: str
   password: str

   addUnstaged: bool = False
   commitBeforePush: bool = False
   pushAfterCommit: bool = False
   pullExistingWhileClone: bool = False

   commands: List[Commands] = []
   cloneGroups: List[str] = []
   filters: Filters
   localDir: str

   def __init__(self) -> None:
      self.filters = Filters()

   def setFilter(
       self,
       forks: bool,
       private: bool,
       owner: bool,
       dirty: bool,
       ahead: bool,
       behind: bool,
       listOnly: bool = None,
       remoteOnly: bool = None
   ):
      self.filters.forks = forks
      self.filters.private = private
      self.filters.owner = owner
      self.filters.dirty = dirty
      self.filters.ahead = ahead
      self.filters.behind = behind
      if listOnly != None:
         self.filters.listOnly = listOnly
      if remoteOnly != None:
         self.filters.remoteOnly = remoteOnly

   def isGithubRequired(self) -> bool:
      if self.filters.forks != None:
         return True
      elif self.filters.owner != None:
         return True
      elif self.filters.private != None:
         return True
      elif self.filters.remoteOnly != None:
         return True
      else:
         return False
