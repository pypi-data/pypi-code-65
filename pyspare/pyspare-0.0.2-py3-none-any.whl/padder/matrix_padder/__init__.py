from aryth.bound_vector import max_by
from crostab import Table
from texting import DA, SP, lange
from veho.columns import mapper as mapper_columns
from veho.matrix.enumerate import mapper
from veho.vector import zipper

from pyspare.padder.string_padder import to_pad


def matrix_padder(matrix, ansi=False, fill=SP):
    pad = to_pad(ansi=ansi, fill=fill)
    length = lange if ansi else len
    widths = mapper_columns(matrix, lambda col: max_by(col, indicator=length))
    return mapper(matrix, lambda x, i, j: pad(x, widths[j], x))

