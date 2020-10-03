"""A dropdown selection widget."""

from __future__ import annotations
import logging
from typing import Callable, Optional, Sequence

import wx
from aio_wx_widgets import type_annotations as T
from aio_wx_widgets.core.binding import Bindable

_LOGGER = logging.getLogger(__name__)

__all__ = ["Select"]


class Select(Bindable):
    """Dropdown selection widget."""

    def __init__(
        self,
        choices: Sequence[T.Choice],
        on_select_callback: Optional[Callable[[T.Choice], None]] = None,
        binding: Optional[T.Binding] = None,
    ):
        """
        Init.

        Args:
            choices: Used to populate the dropdown.
            on_select_callback: called when selection is made.
            binding:
        """
        super().__init__(binding)
        self.choices = choices
        self._on_select_callback = on_select_callback
        self._selected_item = None

        self.ui_item = wx.Choice()
        self.ui_item.Bind(wx.EVT_CHOICE, self._on_choice)
        self.ui_item.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)

    def _on_mouse_wheel(self, evt):
        """Capturing as I want to disable selection when scrolling"""

    def init(self, parent):
        """Initialize the component."""
        self.ui_item.Create(parent, choices=[choice.label for choice in self.choices])

    def _set_ui_value(self, value: T.Choice):
        try:
            _idx = next(
                (i for i, val in enumerate(self.choices) if val.value == value.value)
            )
        except StopIteration:
            _LOGGER.error("Default product not available")
        else:
            self.ui_item.Select(_idx)

    def _on_choice(self, event):
        _idx = self.ui_item.GetSelection()
        _LOGGER.debug("Selected idx: %s", _idx)
        self._selected_item = self.choices[_idx]
        self._on_ui_change()
        if self._on_select_callback:
            self._on_select_callback(self._selected_item)

    def _get_ui_value(self, force):
        return self._selected_item

    def __call__(self, parent):
        self.init(parent)
        self._make_binding()

        return self
