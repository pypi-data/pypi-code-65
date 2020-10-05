"""Start pytentiostat."""


# --- import --------------------------------------------------------------------------------------


import appdirs
import os
import shutil

from pytentiostat.widgets import main_window


# --- define --------------------------------------------------------------------------------------


here = os.path.abspath(os.path.dirname(__file__))
base = os.path.dirname(os.path.dirname(here))


# --- main ----------------------------------------------------------------------------------------


def main():
    """Start yaq application."""
    # create app data directory
    d = os.path.join(appdirs.user_data_dir(), "pytentiostat")
    if not os.path.isdir(d):
        os.mkdir(d)
    # begin
    main_window.main()


if __name__ == "__main__":
    main()
