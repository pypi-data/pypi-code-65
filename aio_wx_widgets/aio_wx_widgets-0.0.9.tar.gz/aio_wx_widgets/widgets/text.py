"""Text widgets."""

import logging
from typing import Optional

import wx

from aio_wx_widgets.core.binding import Bindable
from aio_wx_widgets.colors import GREEN
from aio_wx_widgets.const import is_debugging

_LOGGER = logging.getLogger(__name__)

__all__ = ["Text"]


def _get_font_info(current_font: wx.Font, font_size: float = 1, bold=False) -> wx.Font:
    font = wx.Font()

    if font_size != 1:
        current_font_size = current_font.GetPointSize()
        new_font_size = int(font_size * current_font_size)
        font.SetPointSize(new_font_size)
        # font_info=wx.FontInfo(new_font_size)
    # else:
    #     font_info=wx.FontInfo()

    if bold:
        font.MakeBold()
        # font_info.Weight(wx.FONTWEIGHT_BOLD)

    return font


class Text(Bindable):
    """Static text."""

    def __init__(
        self,
        text="",
        font_size: float = 1,
        color: Optional[int] = None,
        binding=None,
        bold=False,
    ):
        """Init.

        Args:
            parent:
            text:
            font_size:
        """
        self._color = color
        self._text = text

        super().__init__(binding)

        self.ui_item = wx.StaticText()

        self._font = _get_font_info(self.ui_item.GetFont(), font_size, bold=bold)

    def _set_ui_value(self, value):
        self.ui_item.SetLabelText(str(value))

    def _get_ui_value(self, force: bool):
        """This is a one way binding. Not implementing this."""
        return None

    def __call__(self, parent):
        self.ui_item.Create(parent)
        if self._font:
            self.ui_item.SetFont(self._font)

        self.set_text(self._text, self._color)
        if is_debugging():
            self.ui_item.SetBackgroundColour(GREEN)
        self._make_binding()
        return self

    def set_text(self, text, color=None):
        """Set text."""
        self._text = str(text)
        self.ui_item.SetLabel(self._text)
        if color:
            self.ui_item.SetForegroundColour(color)
