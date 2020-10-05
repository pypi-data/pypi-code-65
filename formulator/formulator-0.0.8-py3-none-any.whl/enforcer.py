#!/usr/bin/env python

## Standard Lib
from collections import OrderedDict
from functools import wraps
import logging
import re

## TTILS:
from .terrors import *
from .conf import *

def export(code):
    globals()[code.__name__] = code
    __all__.append(code.__name__)
    return code

__all__ = []


def validate(argname, annotation, argument):
    code_block = f'''
class Struct:
    value = {annotation.__doc__}()
tester = Struct()
tester.value = {argument}
'''
    try:
        exec(code_block)
    except Exception as e:
        return e, argname
    return 0

@export
def typeCheck(func):
    '''Workhorse wrapper function that does type checking. Will not return any of the errors if global error variable is set to False.'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if func.__annotations__:
            ##Before operations, preserve the order matching the passing of the arguments.
            ##Construct the set that belong to formulator:
            annotations = OrderedDict(
                {k: v for k, v in func.__annotations__.items() if hasattr(v, '_validator_type')})
            if "return" in annotations.keys():
                return_constraint = annotations.pop("return")
            errors = []
            for annote, val in zip(annotations.items(), args):
                rval = validate(annote[0], annote[1], val)
                if rval != 0:
                    errors.append(rval)
        result_set = func(*args, **kwargs), errors
        rval = validate("returned value", return_constraint, result_set[0])
        if rval != 0:
            errors.append(rval)
        if errors and DEBUG:
            print(errors)
        return result_set[0]
    return wrapper
