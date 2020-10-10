#!/usr/bin/env python3
import os
import io
from yaml import load as yaml_load
try:
    # use C version if possible for speedup
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


def yaml_loader(yaml_file):
    """Return dictionary of yaml file provided

    Keyword Arguments:
    - yaml_file(str): relative or full path to yaml file
    """
    if os.path.exists(yaml_file):
        with open(yaml_file, 'rb') as _file:
            return yaml_load(_file, Loader=SafeLoader) or {}

    else:
        # need to figure out a common error raising strategy
        pass
