# Wrappers for optional dependencies

from typing import Iterable


def tqdm(*args, **kwargs) -> Iterable:
    """
    tqdm wrapper, also works without tqdm installed
    :param args: arguments to tqdm. first argument is returned if tqdm is unavailable and kwargs does not contain the 'iterable' key
    :param kwargs: keyword arguments to tqdm
    :return:an iterable with tqdm progress bar, if tqdm is available. otherwise just returns the given iterable
    """
    try:
        from tqdm import tqdm
        return tqdm(*args, **kwargs)
    except ImportError:
        if 'iterable' in kwargs:
            return kwargs['iterable']
        else:
            return args[0]
