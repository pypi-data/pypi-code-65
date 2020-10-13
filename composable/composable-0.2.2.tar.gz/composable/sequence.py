from composable.pipeable import pipeable
from itertools import islice

@pipeable
def to_list(iter):
    ''' converts any iterable sequence into a list.

    Args:
        iter: an finite iterable sequence of items

    Returns:
        A list of the sequence iter, which maintains the original order
    '''
    return list(iter)


toList = to_list


@pipeable
def to_tuple(iter):
    ''' converts any iterable sequence into a tuple.

    Args:
        iter: an finite iterable sequence of items

    Returns:
        A tuple of the sequence iter, which maintains the original order
    '''
    return tuple(iter)


toTuple = to_tuple


built_in_slice = slice


@pipeable
def slice(start, stop, seq, step = 1):
    ''' Slices a seq, equivalent to seq[from_:up_to]

    Args:
        start: starting index for the slice.
        stop: final index
        step: the step size (can only be negative if seq supports slicing)
        seq: a sequence of value that supports slicing, e.g. list, tuple, or string

    Returns:
        A seq that is a subsequence of seq that starts at index `from_` 
        and includes all values up to, but not includeing `up_to`
        The returned value will be the same type as the input if slicing is supported, 
        otherwise this returns an iterable sequence.
    '''
    try:
        return seq[built_in_slice(start, stop, step)]
    except:
        if step <= 0:
            raise ValueError("Step must be positive for iterators that don't support slicing.")
        return islice(seq, start, stop, step)


@pipeable
def join(sep, L):
    ''' Joins a sequence of str by combining successive elements with sep.

    Args:
        : starting index for the slice.
        up_to: final index

    Returns:
        A list that is a subsequence of L that starts at index `from_` 
        and includes all values up to, but not includeing `up_to`
    '''
    return sep.join(L)


@pipeable
def head(n, seq):
    ''' Returns a list with the first n entries of seq, equivalent to seq[0:up_to]

    Args:
        from_: starting index for the slice.
        up_to: final index
        seq: a sequence of value that supports slicing, e.g. list, tuple, or string

    Returns:
        A seq that is a subsequence of seq that starts at index `from_` 
        and includes all values up to, but not includeing `up_to`
    '''
    return slice(0, n, 1, seq)


@pipeable
def tail(n, seq):
    ''' Returns a list with the last n entries of seq, equivalent to seq[0:up_to]

    Args:
        from_: starting index for the slice.
        up_to: final index
        seq: a sequence of value that supports slicing, e.g. list, tuple, or string

    Returns:
        A seq that is a subsequence of seq that starts at index `from_` 
        and includes all values up to, but not includeing `up_to`
    '''
    try:
        _ = len(seq)
    except:
        raise ValueError("tail needs a sequence that supports len and slicing")
    return seq[built_in_slice(n, len(seq), 1)]