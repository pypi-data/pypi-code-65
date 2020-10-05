#!/usr/bin/env python

## Standard Lib
from collections import OrderedDict
from functools import wraps
import logging
import re

## TTILS:
from .terrors import *
from .conf import *
from .validation import *

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
            do_validate = True
        else:
            do_validate = False
        if do_validate:
            ##Before operations, preserve the order matching the passing of the arguments.
            ##Construct the set that belong to formulator:
            annotations = OrderedDict({k: v for k, v in func.__annotations__.items() if hasattr(v, '_validator_type')})
            if "return" in annotations.keys():
                return_constraint = annotations.pop("return")
                do_return = True
            else:
                do_return = False
            errors = []
            for annote, val in zip(annotations.items(), args):
                rval = validate(annote[0], annote[1], val)
                if rval != 0:
                    errors.append(rval)
        result_set = func(*args, **kwargs)
        if do_validate and do_return:
            rval = validate("returned value", return_constraint, result_set)
            if (rval != 0):
                errors.append(rval)
        if do_validate and FORMDEBUG:
            if errors:
                for i in errors:
                    print(i)
            else:
                pass
        return result_set
    return wrapper
