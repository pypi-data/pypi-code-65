
class Filters:

   # Default with forks. -f = Forks only. -nf = Without forks')
   forks: bool = None
   # Default with private and public. -p = Private only. -np = Public only
   private: bool = None
   # public: bool = True
   # Default owned and not owned. -o = Owned only. -no = Not owned only.')
   owner: bool = None
   # Default clean and dirty. -d = Dirty only. -nd = Clean only')
   dirty: bool = None
   # safely push. -a = local branch is ahead of remote. -nd = local branch is not ahead of remote
   ahead: bool = None
   ### safely pull. -b = local branch is behind remote. -nd = local branch is not behind remote
   behind: bool = None ### adfd
   ### Print only results. Does not execute any command.
   listOnly: bool = None
