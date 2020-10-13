from .pipeable import pipeable

builtin_map = map

@pipeable
def map(f, iter):
    return builtin_map(f, iter)


builtin_filter = filter

@pipeable
def filter(f, iter):
    return builtin_filter(f, iter)

builtin_zip = zip

@pipeable
def zipOnto(iter1, iter2):
    return builtin_zip(iter1, iter2)


@pipeable
def zipWith(iter2, iter1):
    return builtin_zip(iter1, iter2)


builtin_enumerate = enumerate

@pipeable
def enumerate(iter):
    return builtin_enumerate(iter)