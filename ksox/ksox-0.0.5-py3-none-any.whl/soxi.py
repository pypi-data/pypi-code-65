# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional
import os

# Pip
from kcu import sh

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ Public methods ------------------------------------------------------------ #

def get_sample_rate(path: str, debug: bool = False) -> Optional[int]:
    if not os.path.exists(path):
        if debug:
            print('file \'{}\' dows not exist'.format(path))

        return None

    try:
        return int(sh.sh('soxi -r {}'.format(sh.path(path)).strip(), debug=debug))
    except Exception as e:
        if debug:
            print(e)

        return None

def get_len(path: str, debug: bool = False) -> float:
    try:
        return float(sh.sh('soxi -D {}'.format(sh.path(path))).strip())
    except Exception as e:
        if debug:
            print(e)

        return None
