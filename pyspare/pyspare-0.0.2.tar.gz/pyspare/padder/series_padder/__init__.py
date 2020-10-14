from aryth.bound_vector import max_by
from crostab import Series
from texting import DA, lange
from veho.vector import mapper

from pyspare.padder.string_padder import to_lpad, to_rpad


def series_padder(series: Series, ansi, full_angle):
    lpad = to_lpad(ansi=ansi)
    rpad = to_rpad(ansi=ansi)
    length = lange if ansi else len
    pad = max(length(series.title), max_by(series.points, length))
    series = Series(
        title=rpad(series.title, pad),
        rule=DA * pad,
        points=mapper(series.points, lambda x: lpad(x, pad))
    )
    print(series)
    return series
