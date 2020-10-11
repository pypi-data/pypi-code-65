from enum import Enum

class GithubRepositoryType(Enum):
   all = "all",
   owner = "owner",
   public = "public",
   private = "private",
   member = "member"