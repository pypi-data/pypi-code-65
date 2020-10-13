from .pipeable import pipeable
import toolz
import types


def dir_(obj):
    """ Returns a list of all non-dunder methods/attributes of obj.

    args:
        obj: any Python object

    return:
        A list of strings, which represent all methods/attributes that don't start with '__'
    """
    return [m for m in dir(obj) if not m.startswith('__')]


# adapted from https://stackoverflow.com/questions/39184338/how-can-i-decorate-all-functions-imported-from-a-file
def pipeable_all_in_module(module):
    """ decorates all functions in module to be pipeable.
        Will also work with curried functions from toolz.
    """
    for name in dir_(module):
        obj = getattr(module, name)
        if isinstance(obj, toolz.functoolz.curry):
            setattr(module, name, pipeable(obj.func))
        elif isinstance(obj, types.FunctionType):
            setattr(module, name, pipeable(obj))