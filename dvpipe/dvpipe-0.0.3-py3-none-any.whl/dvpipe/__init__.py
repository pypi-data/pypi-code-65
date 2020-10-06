""" dvpipe """


from functools import reduce, partial


__all__ = ['pipe']


def pipe(seed, *funcs):
    """
    Data pipe utility that pipes data from function to function in sequencial order.
    Attributes:
        seed (object): Input to apply to functions.
        *funcs (func): Functions for the input to be passed into.
                        Use tuples for functions with parameters.
    Example:
        pipe({'foo': 'bar'}, func1, func2, (func3, 'test'))
    """
    def return_partial(arg, func):
        args = list(func)
        args.insert(1, arg)
        return partial(*tuple(args))()

    return reduce(lambda arg, func: return_partial(arg, func)
        if isinstance(func, tuple) else func(arg), funcs, seed)
