import os
import stat
from typing import Callable


# TODO Test
def rmtree(path: str, progressCallback: Callable[[float], None]) -> None:
    def _rmtree(path: str, minProgress: float, maxProgress: float) -> None:
        # This is basically a copy of the shutil.rmtree implementation, but with
        #  - simpler error handling (don't need the feature to ignore errors)
        #  - progress callback
        #  - support for removing a file instead of a directory
        if os.path.islink(path):
            # symlinks to directories are forbidden, see bug #1669
            raise OSError("Cannot call rmtree on a symbolic link")

        children = os.listdir(path)
        progressShare = (maxProgress-minProgress)/(len(children)+1)
        currentMinProgress = minProgress
        for name in children:
             fullname = os.path.join(path, name)
             try:
                  mode = os.lstat(fullname).st_mode
             except os.error:
                  mode = 0
             if stat.S_ISDIR(mode):
                  _rmtree(fullname, currentMinProgress, currentMinProgress + progressShare)
             else:
                 os.remove(fullname)
             currentMinProgress = currentMinProgress + progressShare
             progressCallback(currentMinProgress)
        os.rmdir(path)
        progressCallback(maxProgress)

    progressCallback(0)
    if os.path.isfile(path):
        os.remove(path)
        progressCallback(1)
    else:
        _rmtree(path, 0, 1)
