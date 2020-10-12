from composable.pipeable import pipeable

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
def slice(from_, up_to, seq):
    ''' Slices a seq, equivalent to seq[from_:up_to]

    Args:
        from_: starting index for the slice.
        up_to: final index
        seq: a sequence of value that supports slicing, e.g. list, tuple, or string

    Returns:
        A seq that is a subsequence of seq that starts at index `from_` 
        and includes all values up to, but not includeing `up_to`
    '''
    return seq[built_in_slice(from_, up_to)]


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