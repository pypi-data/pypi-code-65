from typing import Callable, Tuple

from intype import has_literal, is_numeric
from texting.str_value import str_value


def duobound(
        vec: list,
        opt_x: Tuple[Callable, Callable] = (is_numeric, float),
        opt_y: Tuple[Callable, Callable] = (has_literal, str_value)
):
    size = len(vec)
    vec_x, hi_x, (filter_x, mapper_x) = [None] * size, 0, opt_x
    vec_y, hi_y, (filter_y, mapper_y) = [None] * size, 0, opt_y
    max_x = max_y = min_x = min_y = None
    for i, v in enumerate(vec):
        if filter_x(v) and (hi_x := hi_x + 1):
            vec_x[i] = v = mapper_x(v) if mapper_x else v
            if min_x is None: max_x = min_x = v
            if v > max_x: max_x = v
            elif v < min_x: min_x = v
        elif filter_y(v) and (hi_y := hi_y + 1):
            vec_y[i] = v = mapper_y(v) if mapper_y else v
            if min_y is None: max_y = min_y = v
            if v > max_y: max_y = v
            elif v < min_y: min_y = v
    return {'slice': vec_x, 'min': min_x, 'max': max_x, 'count': hi_x}, \
           {'slice': vec_y, 'min': min_y, 'max': max_y, 'count': hi_y}
