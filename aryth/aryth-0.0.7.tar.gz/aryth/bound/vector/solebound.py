from typing import Callable, Tuple

from intype import is_numeric


def solebound(
        vec: list,
        opt: Tuple[Callable, Callable or None] = (is_numeric, float)
):
    size = len(vec)
    ve, hi, (filter_fn, mapper) = [None] * size, 0, opt
    ma = mi = None
    for i, v in enumerate(vec):
        if filter_fn(v) and (hi := hi + 1):
            ve[i] = v = mapper(v) if mapper else v
            if not ma and not mi: ma = mi = v
            if v > ma:
                ma = v
            elif v < mi:
                mi = v
    return {'slice': ve, 'min': mi, 'max': ma, 'count': hi}
