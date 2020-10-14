from dataclasses import dataclass
from typing import List

from veho.matrix import margin_mapper, margin_mutate, margin_shallow, size
from veho.vector import init

from pyspare.margin.matrix_margin.sizing import sizing
from pyspare.margin.utils import marginal


@dataclass
class MatrixMargin:
    matrix: List[list]
    top: int
    bottom: int
    left: int
    right: int
    height: int
    width: int

    @staticmethod
    def build(mx, tp, bt, lf, rt, ht=None, wd=None) -> 'MatrixMargin':
        (tp, bt, lf, rt, ht, wd) = sizing(mx, tp, bt, lf, rt, ht, wd)
        cut_mx = margin_shallow(mx, tp, bt, lf, rt)
        return MatrixMargin(cut_mx, tp, bt, lf, rt, ht, wd)

    def empty_row(self, el) -> list:
        return init(self.left + self.right, lambda _: el)

    def map(self, fn, mutate=False) -> 'MatrixMargin':
        boot, mapper = (self.reboot, margin_mutate) if mutate else (self.clone, margin_mapper)
        mx, tp, bt, lf, rt = self.matrix, self.top, self.bottom, self.left, self.right
        return boot(mapper(mx, fn, tp, bt, lf, rt))

    def stringify(self, func=None, mutate=False) -> 'MatrixMargin':
        fn = (lambda x: str(func(x))) if func else str
        return self.map(fn, mutate)

    def to_matrix(self, el):
        mx, tp, bt, lf, rt = self.matrix, self.top, self.bottom, self.left, self.right
        dash_x, dash_y = bool(bt), bool(rt)
        upper = [marginal(row, lf, rt, dash_y and el) for row in mx[:tp]] if tp else []
        lower = [marginal(row, lf, rt, dash_y and el) for row in mx[-bt:]] if bt else []
        w = size(upper)[1] or size(lower)[1]
        blank_line = [[el] * w] if w and dash_x and el else []
        return upper + blank_line + lower

    def reboot(self, mx) -> 'MatrixMargin':
        if mx: self.matrix = mx
        return self

    def clone(self, mx) -> 'MatrixMargin':
        tp, bt, lf, rt, ht, wd = self.top, self.bottom, self.left, self.right, self.height, self.width
        return MatrixMargin(mx, tp, bt, lf, rt, ht, wd)
