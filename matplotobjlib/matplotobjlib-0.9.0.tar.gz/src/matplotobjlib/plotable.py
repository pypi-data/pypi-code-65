import abc

from matplotlib.artist import Artist
from matplotlib.axes._axes import Axes


class Plotable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def draw(self, axes: Axes, x_log: bool, y_log: bool) -> Artist:
        pass
