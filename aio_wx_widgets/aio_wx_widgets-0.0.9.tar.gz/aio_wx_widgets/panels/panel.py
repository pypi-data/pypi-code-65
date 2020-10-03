"""Panel. Sits in a frame. Holds widgets."""
from __future__ import annotations

import logging

import wx
from wx.lib.scrolledpanel import ScrolledPanel
from aio_wx_widgets import type_annotations as T
from aio_wx_widgets.core.sizers import PanelMixin, SizerMixin

_LOGGER = logging.getLogger(__name__)


class SimplePanel(PanelMixin, SizerMixin):
    """A simple panel."""

    def __init__(self, parent, scrollable=False, **kwargs):
        """Init."""

        if scrollable:
            self.ui_item = ScrolledPanel(parent)
            self.ui_item.SetupScrolling()
        else:
            self.ui_item = wx.Panel(parent)
        super().__init__()

        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.ui_item.SetSizer(self._sizer)

    @property
    def controller(self) -> T.BaseController:
        raise NotImplementedError()
