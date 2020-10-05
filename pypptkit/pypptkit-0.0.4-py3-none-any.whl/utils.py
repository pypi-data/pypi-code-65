import os
import subprocess
from typing import List

from pptx import Presentation


def ensure_dir(f):
    folder = os.path.dirname(f)
    if folder != '' and not os.path.isdir(folder):
        os.makedirs(folder)


def touch(f):
    if os.path.isfile(f):
        os.utime(f, None)
    else:
        open(f, 'w').close()


def touch_mkdir(f):
    ensure_dir(f)
    touch(f)


def touch_mkdir_many(filenames):
    for filename in filenames:
        touch_mkdir(filename)


def no_err_run(args):
    assert isinstance(args, list)
    subprocess.call(args)


def get_sorted_refs(filenames: List[str]):
    refs = set()
    for filename in filenames:
        presentation = Presentation(filename)
        for slide in presentation.slides:
            for v in slide.part.rels.values():
                target: str = v.target_ref
                if target.startswith(".."):
                    continue
                refs.add(target)
    refs = sorted(list(refs))
    return refs


# noinspection PyUnusedLocal
# pylint: disable=unused-argument
def download(link: str):
    pass
