import collections
from typing import Optional, Sequence

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes._axes import Axes
from pycertainties import uncertainty_str

from matplotobjlib.plotable import Plotable
from matplotobjlib.type_hints import Color, Value
from matplotobjlib.utilities import fit_func


def _make_fit_string(fit_string, values, dvalues):
    strings = []
    for value, dvalue in zip(values, dvalues):
        strings.append(f"({uncertainty_str(value, dvalue)})")
    return fit_string.format(*strings)


class Graph(Plotable):
    """
    Provides values that should be plotted on a subplot. Optionally a linear regression can be calculated for the data

    Attributes:
        x_values: A sequence of values to be plotted on the x axes. Should have the same length as y_values
        y_values: A sequence of values to be plotted on the y axes. Should have the same length as x_values
        regression: If this is true this will draw a linear regression for the plot
        legend_label: If a string is provided the graph will be included in the subplot legend

    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        x_values: Sequence[Value],
        y_values: Sequence[Value],
        *,
        x_errors: Optional[Sequence[Value]] = None,
        y_errors: Optional[Sequence[Value]] = None,
        curve_fits=None,
        legend_label: Optional[str] = None,
        color: Optional[Color] = None,
        plot_type: str = "o",
        plot_size: int = 13,
        line_width: int = 1,
    ):
        """
        Creates a new GraphSettings object

        Args:
            x_values: A sequence of values to be plotted on the x axes. Should have the same length as y_values
            y_values: A sequence of values to be plotted on the y axes. Should have the same length as x_values
            regression: If this is true this will draw a linear regression for the plot
            legend_label: If a string is provided the graph will be included in the subplot legend
        """
        if curve_fits is not None and not isinstance(curve_fits, collections.Sequence):
            curve_fits = [curve_fits]
        self.x_values = x_values
        self.y_values = y_values
        self.legend_label = legend_label
        self.plot_type = plot_type
        self.x_error = x_errors
        self.y_error = y_errors
        self.color = color
        self.curve_fits = curve_fits
        self.plot_size = plot_size
        self.line_width = line_width

    def draw(self, axes: Axes, x_log: bool = False, y_log: bool = False) -> Artist:
        # pylint: disable=too-many-locals
        if self.x_error is not None or self.y_error is not None:
            line = axes.errorbar(
                self.x_values,
                self.y_values,
                self.y_error,
                self.x_error,
                self.plot_type,
                ms=self.plot_size,
                color=self.color,
                linewidth=self.line_width,
            )[0]
        else:
            line = axes.plot(
                self.x_values,
                self.y_values,
                self.plot_type,
                ms=self.plot_size,
                color=self.color,
                linewidth=self.line_width,
            )[0]
        if self.curve_fits is not None:
            for fit in self.curve_fits:
                x_values, y_values, x_error, y_error = self.x_values, self.y_values, self.x_error, self.y_error
                if x_log:
                    x_values = np.log(self.x_values)
                    x_error = np.log(self.x_error) if self.x_error else self.x_error
                if y_log:
                    y_values = np.log(self.y_values)
                    y_error = np.log(self.y_error) if self.y_error else self.y_error
                optimal, stddev = fit_func(
                    fit.func, x_values, y_values, x_error, y_error, limits=fit.limits, guesses=fit.guesses
                )
                fit.values = optimal
                fit.dvalues = stddev
                trimmed = self.x_values[fit.limits] if fit.limits else self.x_values
                original_xs = np.linspace(min(trimmed), max(trimmed), 1000)
                xs = np.log(original_xs) if x_log else original_xs
                ys = fit.func(xs, *optimal)
                if y_log:
                    ys = np.e ** ys
                regression = axes.plot(original_xs, ys)[0]
                regression.set_color(line._color)  # pylint: disable=protected-access
                if fit.string:
                    name = " for " + self.legend_label if self.legend_label is not None else ""
                    print(f"Best-fit{name}: {_make_fit_string(fit.string, optimal, stddev)}")

        if self.legend_label is not None:
            if self.curve_fits is not None:
                regression.set_label(self.legend_label)
            else:
                line.set_label(self.legend_label)

        return line
