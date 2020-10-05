__all__ = ["Bool"]


from qtpy import QtCore, QtGui, QtWidgets
from ._base import Base


class Bool(Base):
    qtype = "bool"

    def __init__(self, value=False, *args, **kwargs):
        super().__init__(value=value, *args, **kwargs)

    def give_control(self, control_widget):
        self.widget = control_widget
        # set
        self.widget.setChecked(self.value.get())
        # connect signals and slots
        self.updated.connect(lambda: self.widget.setChecked(self.value.get()))
        self.widget.stateChanged.connect(lambda: self(value=self.widget.isChecked()))
        # finish
        self.widget.setToolTip(self.tool_tip)
        self.widget.setDisabled(self.disabled)
        self.has_widget = True
