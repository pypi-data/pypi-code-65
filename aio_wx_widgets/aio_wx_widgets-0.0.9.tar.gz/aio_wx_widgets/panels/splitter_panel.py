"""A panel with a vertical splitter."""

from __future__ import annotations

import logging

import wx
from wx.lib import scrolledpanel

from aio_wx_widgets.core.sizers import SizerMixin

_LOGGER = logging.getLogger(__name__)


class _ScrollPanel(SizerMixin):
    """Panel with scrolling capabilities.

    Used with the TwoSplitterWindow
    """

    def __init__(self, parent):
        self.ui_item = scrolledpanel.ScrolledPanel(parent)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.ui_item.SetSizer(self._sizer)
        self.ui_item.SetupScrolling()

        super().__init__()

    @property
    def sizer(self):
        """Return the sizer of this panel."""
        return self._sizer


class _SplitterPanel(SizerMixin):
    """Splitter panel.

    Used with the TwoSplitterWindow
    """

    def __init__(self, parent):
        self.ui_item = wx.Panel(parent)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.ui_item.SetSizer(self._sizer)

        super().__init__()

    @property
    def sizer(self):
        """Return the sizer of this panel."""
        return self._sizer


class TwoSplitterWindow(SizerMixin):
    """A two splitter window."""

    def __init__(
        self,
        parent,
        window_one_width=250,
        splitter_one_scrollable=True,
        splitter_two_scrollable=True,
    ):
        """Init.

        Args:
            parent:
            window_one_width:
        """

        self.ui_item = wx.SplitterWindow(parent)
        super().__init__()
        if splitter_one_scrollable:
            self.splitter_window_one = _ScrollPanel(self.ui_item)
        else:
            self.splitter_window_one = _SplitterPanel(self.ui_item)
        if splitter_two_scrollable:
            self.splitter_window_two = _ScrollPanel(self.ui_item)
        else:
            self.splitter_window_two = _SplitterPanel(self.ui_item)

        self.ui_item.SetMinimumPaneSize(40)

        self.ui_item.SplitVertically(
            self.splitter_window_one.ui_item,
            self.splitter_window_two.ui_item,
            window_one_width,
        )
        self._sizer = self.splitter_window_one.sizer
        self._parent = self.splitter_window_one.ui_item

    def hide_window2(self):
        """Hide the second window."""
        self.ui_item.Unsplit(self.splitter_window_two.ui_item)

    def show_window2(self):
        """Show the second window."""
        if self.ui_item.IsSplit():
            _LOGGER.debug("Window is already split.")
            return

        self.ui_item.SplitVertically(
            self.splitter_window_one.ui_item, self.splitter_window_two.ui_item
        )

    @property
    def is_split(self) -> bool:
        return self.ui_item.IsSplit()
