# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import List
import os

# Pip
from kcu import sh

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ Public methods ------------------------------------------------------------ #

def change_sample_rate(in_path: str, out_path: str, sample_rate: int, debug: bool = False) -> bool:
    sh.sh('sox {} -r {} {}'.format(sh.path(in_path), sample_rate, sh.path(out_path)), debug=debug)

    return os.path.exists(out_path)

def concat(in_paths: List[str], out_path: str, debug: bool = False) -> bool:
    sh.sh('sox {} {}'.format(' '.join([sh.path(p) for p in in_paths]), sh.path(out_path)), debug=debug)

    return os.path.exists(out_path)

def mix(in_paths: List[str], out_path: str, debug: bool = False) -> bool:
    sh.sh('sox -m {} {}'.format(' '.join([sh.path(p) for p in in_paths]), sh.path(out_path)), debug=debug)

    return os.path.exists(out_path)