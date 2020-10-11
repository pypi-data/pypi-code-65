import enum
from typing import Optional, Tuple

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes._axes import Axes

from matplotobjlib.plotable import Plotable
from matplotobjlib.type_hints import Value


class LogType(enum.Enum):
    Neither = enum.auto()
    X = enum.auto()
    Y = enum.auto()
    Both = enum.auto()


class SubPlot:
    """
    Creates a holder class that stores the info to make a single matplotlib subplot. Many GraphSettings could be added
    and various configurations can be changed

    Attributes:
        graphs: A list of GraphSettings that should be plotted
        x_label: The label for the x-axis of this subplot
        y_label: The label for the y-axis of this subplot
        title: The title for this subplot
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        *plotables: Plotable,
        x_label: str = "",
        y_label: str = "",
        title: str = "",
        log: Optional[LogType] = None,
        tick_size: Optional[int] = None,
        axis_label_size: int = 23,
        title_font_size: int = 23,
        legend_size: Optional[int] = None,
        x_range: Optional[Tuple[Optional[Value], Optional[Value]]] = None,
        y_range: Optional[Tuple[Optional[Value], Optional[Value]]] = None,
    ):
        """
        Creates a new SubPlot object

        Args:
            args: A list of GraphSettings may be provided or they may be provided separately and collected
            x_label: The label for the x-axis of this subplot
            y_label: The label for the y-axis of this subplot
            title: The title for this subplot
        """
        self.plotables = list(plotables)
        self.x_label = x_label
        self.y_label = y_label
        self.title = title
        self.x_log = log in (LogType.X, LogType.Both)
        self.y_log = log in (LogType.Y, LogType.Both)
        self.tick_size = tick_size
        self.axis_label_size = axis_label_size
        self.title_size = title_font_size
        self.legend_size = legend_size
        self.x_range = x_range
        self.y_range = y_range
        self._axis = None

    def set_axis(self, ax: Axes) -> None:
        self._axis = ax
        ax.set_ylabel(self.y_label, fontsize=self.axis_label_size)
        ax.set_xlabel(self.x_label, fontsize=self.axis_label_size)
        ax.set_title(self.title, fontsize=self.title_size, fontweight="bold")
        ax.ticklabel_format(axis="y", style="sci")
        ax.ticklabel_format(useOffset=False)
        if self.tick_size:
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(self.tick_size)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(self.tick_size)
        if self.x_log:
            ax.set_xscale("log", basey=np.e)
            ax.grid(which="major")
        if self.y_log:
            ax.set_yscale("log", basey=np.e)
            ax.grid(which="minor")
        if self.x_range is not None:
            ax.set_xlim(*self.x_range)
        if self.y_range is not None:
            ax.set_ylim(*self.y_range)

    def draw(self) -> None:
        has_labels = False
        for plotable in self.plotables:
            artist = plotable.draw(self._axis, self.x_log, self.y_log)
            if not artist.get_label().startswith("_"):
                has_labels = True

        if has_labels:
            self._axis.legend(loc="best", fontsize=self.legend_size)

    def add_plotable(self, plotable: Plotable) -> Optional[Artist]:
        self.plotables.append(plotable)
        if self._axis:
            handle = plotable.draw(self._axis, self.x_log, self.y_log)
            self._axis.legend()
            return handle
