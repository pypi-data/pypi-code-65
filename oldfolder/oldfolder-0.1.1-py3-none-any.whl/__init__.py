"""
Provides functions that can be combined to move old subdirectories containing files
which haven't been modified for a given number of years.

Old subdirectories are placed in a storage folder located in their parent directory.
Moves can also be specified based on created or accessed time.

"""
from .oldfolder import prepare_move
from .oldfolder import move_files


__all__ = ["prepare_move", "move_files"]