from .pipeable import pipeable


@pipeable
def map(f, L):
    ''' applies f to all elements of L, immediately returning a list of the resulting values.

    Args:
        f: A unary function
        L: A list of values

    Returns:
        A list of the results of f applied to each element of L.
        Note that this is a strict version of the built-in map (which returns a generator).
    '''
    return [f(x) for x in L]


@pipeable
def filter(p, L):
    ''' Filters the elements of L, returning a list of all elements that pass the predicate p.

    Args:
        p: a unary boolean function used to filter the list
        L: A list of values

    Returns:
        A list of the elements of L that satisfy p.
        Note that this is a strict version of the built-in filter (which returns a generator).
    '''
    return [x for x in L if p(x)]


@pipeable
def zipWith(iter2, iter1):
    ''' zips the elements of iter1 and iter2 into a list of tuples of the form (i1, i2)

    args:
        iter2: a list of values
        iter1: a list of values

    returns:
        a list of tuples of the form (i1, i2).  this is similar to zip(iter1, iter2).
        note that
        1. the order is reversed for more natural piping, 
           that is iter1 >> zipwith(iter2) has the values of iter1 first, i.e. (i1, i2)
        2. performs strict application, where the built-in zip returns a generator.
    '''
    return [ (i1, i2) for i2, i1 in zip(iter2, iter1)]


@pipeable
def zipOnto(iter1, iter2):
    ''' zips the elements of iter1 and iter2 into a list of tuples of the form (i2, i1)

    args:
        iter1: a list of values
        iter2: a list of values

    returns:
        a list of tuples of the form (i1, i2).  this is similar to zip(iter1, iter2).
        note that
        1. the order is the same as the built-in zip, meaning piping will reverse the order
           that is iter1 >> zipOnto(iter2) has the values of iter1 first, i.e. (i2, i1)
        2. performs strict application, where the built-in zip returns a generator.
    '''
    return list(zip(iter1, iter2))

enum = enumerate

@pipeable
def enumerate(iter):
    ''' generates a list of tuples, pairing each value with its index, (index, value)

    Args:
        iter: A sequence of values

    Returns:
        A list of tuples of the form (index, value), which correspond to the index and value
        of each entry of iter.
        Note that this is a strict version of the built-in enumerate (which returns a generator).
    '''
    return list(enum(iter))
