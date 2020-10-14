"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the PyInventory team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
from pathlib import Path


class VirtualEnvPath:
    def __init__(self):
        # print("sys.executable:", sys.executable)
        # print("sys.prefix:", sys.prefix)
        # print("sys.real_prefix:", getattr(sys, "real_prefix", None))

        self.env_path = Path(sys.prefix)  # e.g.: /home/<username>/DjangoInventoryEnv
        assert self.env_path.is_dir()

    def get_inventory_exe(self):
        if sys.platform in ("win32", "cygwin"):
            inventory_filename = "inventory.exe"
        else:
            inventory_filename = "inventory"

        self.executable_path = Path(sys.executable)  # e.g.: /home/<username>/DjangoInventoryEnv/bin/python3
        assert self.executable_path.is_file()

        # raise ValueError if self.env_path is not a subpath of self.executable_path
        self.executable_path.relative_to(self.env_path)

        inventory_exe = Path(self.executable_path.parent, inventory_filename)
        assert inventory_exe.is_file(), "for_runner executeable not found here: '%s'" % inventory_exe
        assert os.access(str(inventory_exe), os.X_OK), "File not executeable: '%s'" % inventory_exe

        return inventory_exe


def get_venv_path():
    """
    :return: VirtualEnv root dir, e.g.: /home/<username>/DjangoInventoryEnv
    """
    return VirtualEnvPath().env_path
