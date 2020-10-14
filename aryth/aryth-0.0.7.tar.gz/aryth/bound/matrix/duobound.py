from typing import Callable, List, Tuple

from intype import has_literal, is_numeric
from veho.matrix import iso, size
from texting.str_value import str_value


def duobound(
        mx: List[list],
        opt_x: Tuple[Callable, Callable] = (is_numeric, float),
        opt_y: Tuple[Callable, Callable] = (has_literal, str_value)
):
    h, w = size(mx)
    mx_x, hi_x, (filter_x, mapper_x) = iso(h, w, None), 0, opt_x
    mx_y, hi_y, (filter_y, mapper_y) = iso(h, w, None), 0, opt_y
    max_x = max_y = min_x = min_y = None
    for i, row in enumerate(mx):
        for j, v in enumerate(row):
            if filter_x(v) and (hi_x := hi_x + 1):
                mx_x[i][j] = v = mapper_x(v) if mapper_x else v
                if min_x is None: max_x = min_x = v
                if v > max_x: max_x = v
                elif v < min_x: min_x = v
            elif filter_y(v) and (hi_y := hi_y + 1):
                mx_y[i][j] = v = mapper_y(v) if mapper_y else v
                if min_y is None: max_y = min_y = v
                if v > max_y: max_y = v
                elif v < min_y: min_y = v
    return {'slice': mx_x, 'min': min_x, 'max': max_x, 'count': hi_x}, \
           {'slice': mx_y, 'min': min_y, 'max': max_y, 'count': hi_y}
