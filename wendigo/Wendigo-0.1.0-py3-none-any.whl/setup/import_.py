from clr import AddReference
from glob import glob
from pathlib import Path

__all__ = []

def import_dll():
    """
    Import Dlls.
    """
    paths = [
        "System.Drawing",
        "System.Windows.Forms",
    ] + glob(str(Path(__file__).parents[1].joinpath("bin/x64/*.dll")))

    for path in paths:
        AddReference(path)

import_dll()