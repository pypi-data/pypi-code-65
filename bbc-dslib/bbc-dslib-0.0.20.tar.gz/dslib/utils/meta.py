from typing import Any


def resolve(name: str) -> Any:
    """
    Loads a variable, function, class or module from a given dotted path (e.g. 'dslib.utils.resolve').
    Copied directly from: https://github.com/python/cpython/blob/master/Lib/logging/config.py
    :param name: (str) name (or dotted path) of the element to be imported
    :return: loaded class, function or module
    """
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)
    return found
