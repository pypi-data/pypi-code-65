from __future__ import annotations

import logging

import wx

from aio_wx_widgets import type_annotations as T
from aio_wx_widgets.core.binding import Binding
from aio_wx_widgets.panels.panel import SimplePanel
from aio_wx_widgets.core.sizers import AlignHorizontal
from aio_wx_widgets.widgets.button import AioButton
from aio_wx_widgets.containers.grid import Grid, VERTICAL
from aio_wx_widgets.widgets.select import Select
from aio_wx_widgets.widgets.text import Text
from aio_wx_widgets.widgets.text_entry import Entry

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from demo.controller.controller_two import ControllerTwo

_LOGGER = logging.getLogger(__name__)


class ViewTwo(SimplePanel):
    """Second view."""

    def __init__(self, parent, controller):
        self._controller = controller
        super().__init__(parent)
        self._text = Text("This is text that changes as a result of an event happening")

        # self._controller.add_task(self._controller.add_to_log.subscribe(self._add_to_log))
        self.controller.add_to_log.publish += self._add_to_log

        self._callback_text = Text("Nothing selected yet")
        self._bound_selected_item = Text("Nothing selected yet")

    @property
    def controller(self) -> ControllerTwo:
        return self._controller

    def populate(self):
        self.add(
            Entry(binding=Binding(self._controller, "value_1")), margin=(10, 10, 5, 20),
        )
        self.add(Entry(binding=Binding(self._controller, "value_1")))
        self.add(
            AioButton("test button with normal function as callback", self._press),
            margin=(10, 10, 5, 20),
        )
        self.add(self._text)

        # It is possible to add bare wx-python widgets.
        self.add(wx.StaticLine(parent=self.ui_item), create=False)

        with self.add(Grid()) as grd:
            grd.add(
                Text("This is a selection dropdown"),
                weight=4,
                align_horizontal=AlignHorizontal.right,
            )
            with grd.add(Grid(orientation=VERTICAL), weight=6) as grd:
                grd.add(
                    Select(
                        self.controller.choices,
                        on_select_callback=self._on_select_callback,
                        binding=self.bind("selected_item"),
                    ),
                    align_horizontal=AlignHorizontal.left,
                )
                grd.add(Text("Selection based on callback:"))
                grd.add(self._callback_text)
                grd.add(Text("Selection based on binding value:"))
                grd.add(
                    AioButton(
                        label="Display bound value", callback=self._show_bound_value
                    )
                )
                grd.add(self._bound_selected_item)

    def _show_bound_value(self, evt):
        self._bound_selected_item.set_text(self._controller.selected_item)

    def _on_select_callback(self, choice: T.Choice):
        self._callback_text.set_text(str(choice))

    def _press(self, evt):
        self._add_to_log("button pressed.")

    def _add_to_log(self, item: str):
        self._text.set_text(item)
