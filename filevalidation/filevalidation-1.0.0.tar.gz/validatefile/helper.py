"""
Module with helper functions to assit in file validation
"""

__Author__ = "Ram J"
__PyVersion__ = 3


import re


def isempty(value: str) -> bool:
    """
    Function that checks value for emptiness
    """
    return True if value.strip() == '' else False


def isnumeric(value: str) -> bool:
    """
    Function that checks for numeric
    """
    try:
        val = eval(value)
    except Exception:
        return False
    if isinstance(val, int) or isinstance(val, float):
        return True
    else:
        return False


def isinteger(value: str) -> bool:
    """
    Function that checks for interger
    """
    try:
        val = eval(value)
    except Exception:
        return False
    if isinstance(val, int):
        return True
    else:
        return False


def isdecimal(value: str) -> bool:
    """
    Function that checks for decimal
    """
    try:
        val = eval(value)
    except Exception:
        return False
    if isinstance(val, float):
        return True
    else:
        return False


def isexpectedformat(string: str, pattern: str, count: int = None,
                     ignorecase: bool = False) -> bool:
    """
    Function that checks for the given format.
    Providing optional parameter count will check for the number of occurences
    """
    if count is not None and count == 0:
        raise ValueError('If provided, count should be greater than zero')
    if count:
        if ignorecase:
            pattern = re.compile(pattern=pattern, flags=re.IGNORECASE)
        else:
            pattern = re.compile(pattern=pattern)
        res = pattern.findall(string=string)
        if res and (len(res) == count):
            return True
    else:
        if ignorecase:
            pattern = re.compile(pattern=pattern, flags=re.IGNORECASE)
        else:
            pattern = re.compile(pattern=pattern)
        res = pattern.fullmatch(string=string)
        if res:
            return True
    return False


def isexpectedlength(value: str, maxvalue: int, minvalue: int = None) -> bool:
    """
    Function that checks for expected length
    Value for min length is optional
    """
    length = len(value)
    if minvalue and maxvalue:
        return True if minvalue <= length <= maxvalue else False
    elif maxvalue:
        return True if length <= maxvalue else False
