# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import List, Optional
import os

# Pip
from kcu import sh

# Local
from .models.sox_stats import SoxStats
from . import soxi

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

def get_stats(path: str, debug: bool = False) -> Optional[SoxStats]:
    try:
        return SoxStats(sh.sh('sox {} -n stat'.format(path), debug=debug))
    except Exception as e:
        if debug:
            print(e)

        return None

def adjust_volume(in_path: str, out_path: str, multi: float, debug: bool = False) -> bool:
    sh.sh('sox -v {} {} {}'.format(multi, sh.path(in_path), sh.path(out_path)), debug=debug)

    return os.path.exists(out_path)

def trim(in_path: str, out_path: str, len_s: float, start_s: float = 0, debug: bool = False) -> bool:
    '''if start_s is negative, it will record from the end-start_s'''
    sh.sh('sox {} {} trim {} {}'.format(sh.path(in_path), sh.path(out_path), start_s, len_s), debug=debug)

    return os.path.exists(out_path)

def fade(in_path: str, out_path: str, fade_in_s: float = 0, fade_out_s: float = 0, shape: str = 'q', debug: bool = False) -> bool:
    '''shape can be: 'q', 'h', 't', 'p', 'l' '''
    sh.sh('sox {} {} fade q {} -0 {}'.format(sh.path(in_path), sh.path(out_path), fade_in_s, fade_out_s), debug=debug)

    return os.path.exists(out_path)

def crossfade(in_paths: List[str], out_path: str, temp_folder_path: str, fade_s: float = 0, shape: str = 'q', debug: bool = False) -> bool:
    ext = in_paths[0].split('.')[-1]
    starts = []
    ends = []
    middles = []

    i=0
    for in_path in in_paths:
        len_s = soxi.get_len(in_path)

        if i != 0:
            p0 = os.path.join(temp_folder_path, 'p-' + str(i) + '-0.' + ext)
            pf0 = os.path.join(temp_folder_path, 'pf-' + str(i) + '-0.' + ext)
            trim(in_path, p0, fade_s, debug=debug)
            fade(p0, pf0, fade_in_s=fade_s, shape=shape, debug=debug)
            # os.remove(p0)
            starts.append(pf0)
        elif i != len(in_paths) - 1:
            p2 = os.path.join(temp_folder_path, 'p-' + str(i) + '-2.' + ext)
            pf2 = os.path.join(temp_folder_path, 'pf-' + str(i) + '-2.' + ext)
            trim(in_path, p2, fade_s, -fade_s, debug=debug)
            fade(p2, pf2, fade_out_s=fade_s, shape=shape, debug=debug)
            # os.remove(p2)
            ends.append(pf2)

        p1 = os.path.join(temp_folder_path, 'p-' + str(i) + '-1.' + ext)

        if i == 0:
            trim(in_path, p1, len_s - fade_s, debug=debug)
        elif i == len(in_paths) - 1:
            trim(in_path, p1, len_s - fade_s, start_s=fade_s, debug=debug)
        else:
            trim(in_path, p1, len_s - 2*fade_s, start_s=fade_s, debug=debug)

        middles.append(p1)
        i+=1

    fades = []

    for i in range(0, len(starts)):
        p = os.path.join(temp_folder_path, 'f-' + str(i) + '.' + ext)
        mix([starts[i], ends[i]], p, debug=debug)
        fades.append(p)

    parts = []

    for i in range(0, len(middles)):
        parts.append(middles[i])

        if i < len(fades):
            parts.append(fades[i])

    concat(parts, out_path, debug=debug)

    for pp in [starts, ends, parts]:
        for p in pp:
            os.remove(p)

    return os.path.exists(out_path)