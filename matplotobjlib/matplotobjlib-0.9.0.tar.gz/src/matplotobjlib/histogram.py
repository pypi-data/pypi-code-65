from typing import Optional

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes._axes import Axes

from matplotobjlib.plotable import Plotable
from matplotobjlib.type_hints import Range, Value


class Histogram(Plotable):
    def __init__(self, values: Value, binwidth: Optional[Range] = None, num_bins: Optional[int] = None):
        if binwidth is not None:
            self.bins = np.arange(min(values), max(values) + binwidth, binwidth)
        elif num_bins is not None:
            self.bins = num_bins
        else:
            self.bins = None
        self.values = values

    def draw(self, axes: Axes, x_log: bool, y_log: bool) -> Artist:
        if self.bins is not None:
            return axes.hist(self.values, bins=self.bins)
        else:
            return axes.hist(self.values)
