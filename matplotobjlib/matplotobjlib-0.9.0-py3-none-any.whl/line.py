import colorsys
from typing import Optional, Tuple

from matplotlib.artist import Artist
from matplotlib.axes._axes import Axes

from matplotobjlib.plotable import Plotable
from matplotobjlib.type_hints import Color, Value


class Line(Plotable):
    __last_hue__ = 0

    def __init__(self, x: Value, label: Optional[str] = None, *, color: Optional[Color] = None):
        self.x = x
        self.label = label
        self.color = color

    @staticmethod
    def reset_color() -> None:
        Line.__last_hue__ = 0

    @staticmethod
    def _next_color() -> Tuple[float, float, float]:
        hue = Line.__last_hue__ / 255
        Line.__last_hue__ = (Line.__last_hue__ + 45) % 255
        return colorsys.hsv_to_rgb(hue, 1.0, 1.0)

    def draw(self, axes: Axes, x_log: bool, y_log: bool) -> Artist:
        color = self.color if self.color else self._next_color()
        line = axes.axvline(x=self.x, color=color)
        if self.label:
            line.set_label(self.label)
        return line
