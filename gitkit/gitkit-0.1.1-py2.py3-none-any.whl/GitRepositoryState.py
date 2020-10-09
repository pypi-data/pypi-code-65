from enum import Flag

class GitRepositoryState(Flag):
   Unknown = 0
   Local = 1
   Remote = 2
   Cloned = Local | Remote

   @property
   def IsLocal(self) -> bool:
      return (self & GitRepositoryState.Local) == GitRepositoryState.Local

   @property
   def IsRemote(self) -> bool:
      return (self & GitRepositoryState.Remote) == GitRepositoryState.Remote

   @property
   def IsCloned(self) -> bool:
      return self  == GitRepositoryState.Cloned

   def __str__(self) -> str:
      if self.IsCloned:
         return "cloned"
      elif self.IsLocal:
         return "local"
      elif self.IsRemote:
         return "remote"
      else:
         return "Unknown"

