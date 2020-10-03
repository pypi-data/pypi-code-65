import logging
import wx

from aio_wx_widgets.core.binding import Bindable, Binding

_LOGGER = logging.getLogger(__name__)

__all__ = ["CheckBox"]


class CheckBox(Bindable):
    def __init__(self, label: str, binding: Binding):
        super().__init__(binding)
        self._label = str(label)
        self.ui_item = wx.CheckBox()

    def _set_ui_value(self, value):
        val = bool(value)
        _LOGGER.debug("Setting value to %s, %s", val, id(self))
        self.ui_item.SetValue(val)

        # setting this value manually as the SetValue command does -in this case-
        # not trigger the _on_ui_change callback.
        self._fire_update_event = True

    def _get_ui_value(self, force: bool):
        val = self.ui_item.GetValue()
        return val

    def __call__(self, parent):
        self.ui_item.Create(parent, label=self._label)
        self.ui_item.Bind(wx.EVT_CHECKBOX, self._on_ui_change)

        self._make_binding()
        return self
