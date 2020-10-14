from typing import Callable, List, Tuple

from intype import is_numeric
from veho.matrix import iso, size


def solebound(
        mx: List[list],
        opt: Tuple[Callable, Callable] = (is_numeric, float)
):
    h, w = size(mx)
    mat, hi, (filter_fn, mapper_fn) = iso(h, w, None), 0, opt
    ma = mi = None
    for i, row in enumerate(mx):
        for j, v in enumerate(row):
            if filter_fn(v) and (hi := hi + 1):
                mat[i][j] = v = mapper_fn(v) if mapper_fn else v
                if mi is None: ma = mi = v
                if v > ma: ma = v
                elif v < mi: mi = v
    return {'slice': mat, 'min': mi, 'max': ma, 'count': hi}
