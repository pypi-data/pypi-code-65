from __future__ import annotations

import logging

from aio_wx_widgets.core.binding import Binding
from aio_wx_widgets.panels.splitter_panel import TwoSplitterWindow
from aio_wx_widgets.core.sizers import AlignHorizontal, PanelMixin, SizerMixin
from aio_wx_widgets.widgets.button import AioButton
from aio_wx_widgets.containers.grid import Grid, VERTICAL
from aio_wx_widgets.containers.group import Group
from aio_wx_widgets.widgets.text import Text
from aio_wx_widgets.widgets.text_entry import Entry

_LOGGER = logging.getLogger(__name__)


class SplitterWindow(TwoSplitterWindow, PanelMixin, SizerMixin):
    def __init__(self, parent, controller, scrollable=False, window_one_width=250):
        super().__init__(
            parent, splitter_one_scrollable=False, splitter_two_scrollable=False
        )
        self._controller = controller
        self.splitter_window_two.add(Text("This is text"))
        self.splitter_window_two.add(Entry(self.bind("value_1")))

    @property
    def controller(self):
        return self._controller


class ViewThree(SplitterWindow):
    def __init__(self, parent, controller):
        self._controller = controller
        super().__init__(parent, controller)

        self.split_button = AioButton("Remove split", self._toggle_window_2)

    @property
    def controller(self):
        return self._controller

    def populate(self):
        """Populate this view."""
        self.splitter_window_one.add(Entry(binding=self.bind("value_1")))
        # Use a context manager for container types like a group or grid.
        # A group is a container with a label and a sizer inside. Inside
        # this sizer widgets, or other containers can be placed.
        with self.add(Group("A labelled container.")) as group:
            group.add(Text(text="A horizontal grid."))

            with group.add(Grid()) as grd:
                # the binding binds to an attribute defined in the controller
                # the weight determines how much space a specific item should consume
                # with respect to the other members of the container.
                grd.add(Entry(binding=self.bind("value_1")), weight=6, margin=3)
                grd.add(Entry(binding=self.bind("value_1")), weight=4, margin=3)
                grd.add(Entry(binding=self.bind("value_1")), weight=4, margin=3)

        with self.add(Group("Any text entry.")) as group:
            group.add(Entry(binding=Binding(self._controller, "a_string_value")))
            group.add(Entry(binding=Binding(self._controller, "a_string_value")))

        with self.add(Grid()) as grd:
            grd.add(AioButton("button one", self._set_value), weight=6)
            grd.add(AioButton("button two,self", self._set_value), weight=6)

        with self.add(Group("Nesting of grids")) as grp:
            with grp.add(Grid()) as grd:
                grd.add(
                    Text(text="Right aligned text"),
                    weight=3,
                    margin=5,
                    align_horizontal=AlignHorizontal.right,
                )
                with grd.add(Grid(VERTICAL), weight=6, margin=0) as vert_grid:
                    vert_grid.add(
                        AioButton("Left aligned button", self._set_value),
                        align_horizontal=AlignHorizontal.left,
                        margin=4,
                    )
                    vert_grid.add(AioButton("Set number entries.", self._set_value))
                    vert_grid.add(
                        Text(text="Center aligned text with a large margin."),
                        margin=(10, 10, 30, 5),
                        align_horizontal=AlignHorizontal.center,
                    )
                    vert_grid.add(
                        AioButton("right aligned button.", self._set_value),
                        weight=2,
                        align_horizontal=AlignHorizontal.right,
                    )

        self.add(AioButton("open other window", self._on_open_second_window))
        self.add_space(2)

        self.add(
            self.split_button, align_horizontal=AlignHorizontal.right,
        )
        self._set_split_button_text()

    def _set_split_button_text(self):
        if self.is_split:
            self.split_button.label = "Close"
        else:
            self.split_button.label = "Open"

    def _toggle_window_2(self, evt):
        if self.is_split:
            self.hide_window2()
        else:
            self.show_window2()
        self._set_split_button_text()

    async def _on_open_second_window(self, evt):
        await self._controller.open_other_window()

    async def _on_open(self, evt):
        await self._controller.open_other_window()

    async def _set_value(self, evt):
        await self._controller.set_value()
