# from .utils import *
# from .utils_ml import *
# from .basics import *
# from .callbacks import *
# from .optimizers import *
# from .hooks import *
# from .dataloaders import *
# from .metrics import *
# from .loss_funcs import *
# from .activation_funcs import *
# from .text import *
# from .model import *


from pathlib import Path
import json


class Config(dict):
    """config object to store task specific information"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set(self, key, val):
        self[key] = val
        setattr(self, key, val)

    def save_to_json(self, output_file):
        json.dump(self.__dict__, open(output_file, "w"),
                  indent=4, sort_keys=True)

    @classmethod
    def from_json(cls, json_path):
        config_dict = json.load(open(json_path, "r"))
        return cls(**config_dict)

    def __repr__(self):
        return json.dumps(self.__dict__, indent=1)


def filter_files(files, include=[], exclude=[], extension_filtering=False):
    """
    filters a list of files based on filenames or extensions
    files: list of files in a directory
    include: only keep these file extensions
    exclude: remove these file extensions
    """
    if extension_filtering:
        if include:
            include = ["."+incl if incl[0] !=
                       "." else incl for incl in include]
            files = [f for f in files if f.suffix in include]

        if exclude:
            exclude = ["."+excl if excl[0] !=
                       "." else excl for excl in include]
            files = [f for f in files if f.suffix not in exclude]
    else:
        if include:
            files = [f for f in files if f.stem in include]
        if exclude:
            files = [f for f in files if f.stem not in exclude]
    return sorted(files)


def ls(x, recursive=False, include=[], exclude=[], extension_filtering=False):
    if not recursive:
        out = list(x.iterdir())
    else:
        out = [o for o in x.glob('**/*')]
    out = filter_files(
        out, include=include, exclude=exclude, extension_filtering=extension_filtering)
    return out


Path.ls = ls


def noop(x):
    return x
