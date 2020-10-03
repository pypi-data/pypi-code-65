from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from aio_wx_widgets.core.binding import Binding
from aio_wx_widgets.core.validators import float_validator, int_validator
from aio_wx_widgets.panels.panel import SimplePanel
from aio_wx_widgets.core.sizers import AlignHorizontal, VertAlign
from aio_wx_widgets.widgets.button import AioButton
from aio_wx_widgets.widgets.checkbox import CheckBox
from aio_wx_widgets.containers.grid import Grid, VERTICAL
from aio_wx_widgets.containers.group import Group, Section
from aio_wx_widgets.widgets.labelled_item import LabelledItem
from aio_wx_widgets.widgets.text import Text
from aio_wx_widgets.widgets.text_entry import Entry


if TYPE_CHECKING:
    from demo.controller.controller_one import ControllerOne

_LOGGER = logging.getLogger(__name__)


class ViewOne(SimplePanel):
    def __init__(self, parent, controller: "ControllerOne"):
        self._controller = controller
        super().__init__(parent, scrollable=True)

    @property
    def controller(self) -> "ControllerOne":
        return self._controller

    # def populate(self):
    #
    #     with self.add(Group("Nesting of grids")) as grp:
    #         with grp.add(Grid()) as grd:
    #             grd.add(
    #                 Text(text="Right aligned text"),
    #                 weight=3,
    #                 align_horizontal=AlignHorizontal.right,
    #                 ver_align=VertAlign.top
    #             )
    #             with grd.add(Grid(VERTICAL), weight=6, margin=0) as vert_grid:
    #                 vert_grid.add(
    #                     AioButton("Left aligned button", self._set_value),
    #                     align_horizontal=AlignHorizontal.left,
    #                     margin=4,
    #                 )
    #                 vert_grid.add(AioButton("Set number entries.", self._set_value))
    #                 vert_grid.add(
    #                     Text(text="Center aligned text with a large margin."),
    #                     margin=(10, 10, 30, 5),
    #                     align_horizontal=AlignHorizontal.right,
    #                 )
    #                 vert_grid.add(
    #                     AioButton("right aligned button.", self._set_value),
    #                     weight=2,
    #                     align_horizontal=AlignHorizontal.right,
    #                 )
    def populate(self):
        """Populate this view."""

        # Use a context manager for container types like a group or grid.
        # A group is a container with a label and a sizer inside. Inside
        # this sizer widgets, or other containers can be placed.
        self.add(
            LabelledItem(
                "Label text",
                Entry(binding=self.bind("float_val"), validator=float_validator),
            )
        )
        with self.add(Section("Float validators")) as sc:
            with sc.add(Grid()) as grd:
                # the binding binds to an attribute defined in the controller
                # the weight determines how much space a specific item should consume
                # with respect to the other members of the container.
                grd.add(
                    Entry(binding=self.bind("float_val"), validator=float_validator,),
                    weight=6,
                )
                grd.add(
                    Entry(binding=self.bind("float_val"), validator=float_validator,),
                    weight=4,
                )
                grd.add(
                    Text(binding=self.bind("float_val")),
                    weight=4,
                    ver_align=VertAlign.center,
                )
        with self.add(Section("Int validators")) as sc:
            sc.add(Text("Only integer values are allowed."))
            with sc.add(Grid()) as grd:
                grd.add(
                    Entry(binding=self.bind("int_val"), validator=int_validator,),
                    weight=6,
                )
                grd.add(
                    Entry(binding=self.bind("int_val"), validator=int_validator,),
                    weight=4,
                )
                grd.add(Text(binding=self.bind("int_val")), weight=4, margin=3)

        with self.add(Grid()) as grd:
            grd.add(Entry(binding=Binding(self._controller, "a_string_value")))
            grd.add(Entry(binding=Binding(self._controller, "a_string_value")))

        with self.add(Grid()) as grd:
            grd.add(AioButton("button one", self._set_value), weight=6)
            grd.add(AioButton("button two,self", self._set_value), weight=6)

        with self.add(Group("Nesting of grids")) as grp:
            with grp.add(Grid()) as grd:
                grd.add(
                    Text(text="Right aligned text"),
                    weight=3,
                    align_horizontal=AlignHorizontal.right,
                    ver_align=VertAlign.center,
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
        self.add(CheckBox("A checkbox", binding=self.bind("a_checkbox_value")))
        self.add(
            CheckBox("The same checkbox value", binding=self.bind("a_checkbox_value"))
        )
        self.add(AioButton("open other window", self._on_open_second_window))
        self.add(AioButton("open third window", self._on_open_third_window))

    async def _on_open_second_window(self, evt):
        await self._controller.open_other_window()

    async def _on_open_third_window(self, evt):
        await self._controller.open_third_window()

    async def _on_open(self, evt):
        await self._controller.open_other_window()

    async def _set_value(self, evt):
        await self._controller.set_value()
