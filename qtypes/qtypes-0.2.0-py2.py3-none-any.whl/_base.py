__all__ = ["Base"]


import qtpy
from qtpy import QtCore, QtGui, QtWidgets


class Value(QtCore.QMutex):
    def __init__(self, initial_value=None):
        QtCore.QMutex.__init__(self)
        self.value = initial_value

    def get(self):
        return self.value

    def set(self, value):
        self.lock()
        self.value = value
        self.unlock()


class Base(QtCore.QObject):
    updated = QtCore.Signal()

    def __init__(self, value=None, name="", disabled=False, *args, **kwargs):
        super().__init__()
        #
        self.has_widget = False
        self.tool_tip = ""
        self.value = Value(value)
        self.disabled = disabled
        self.name = name

    def __call__(self, value=None, **kwargs):
        if value is not None:
            self.value.write(value)
            self.updated.emit()
        return self.value.get()

    def get(self):
        return self.value.get()

    def set_disabled(self, disabled):
        self.disabled = bool(disabled)
        if self.has_widget:
            self.widget.setDisabled(self.disabled)

    setDisabled = set_disabled  # for qt inheritence reasons

    def set_tool_tip(self, tool_tip):
        self.tool_tip = str(tool_tip)
        if self.has_widget:
            self.widget.setToolTip(self.tool_tip)

    def set(self, value):
        self.value.set(value)
        self.updated.emit()
