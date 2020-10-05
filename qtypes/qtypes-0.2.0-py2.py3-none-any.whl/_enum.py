__all__ = ["Enum"]


from qtpy import QtCore, QtGui, QtWidgets
from ._base import Base


class Enum(Base):
    def __init__(self, allowed_values=["None"], initial_value=None, *args, **kwargs):
        super().__init__()
        self.qtype = "enum"
        self.allowed_values = list(allowed_values)
        self.data_type = type(self.allowed_values[0])
        if initial_value is None:
            self.set(self.allowed_values[0])
        else:
            self.set(initial_value)

    def associate(self, display=None, pre_name=""):
        # display
        if display is None:
            display = self.display
        # name
        name = pre_name + self.name
        # new object
        new_obj = Combo(
            initial_value=self.get(),
            display=display,
            allowed_values=self.allowed_values,
            name=name,
        )
        return new_obj

    def get_index(self):
        return self.allowed_values.index(self.get())

    def save(self, value=None):
        if value is not None:
            self.value.set(value)

    def set_allowed_values(self, allowed_values):
        """
        Set the allowed values of the Combo object.

        Parameters
        ----------
        allowed_values : list
            the new allowed values

        Notes
        ----------
        The value of the object is written to the first allowed value if the
        current value is not in the allowed values.
        """
        if allowed_values == self.allowed_values:
            return
        self.allowed_values = list(allowed_values)
        # update widget
        if self.has_widget:
            self.widget.currentIndexChanged.disconnect(self.set_from_widget)
            self.widget.clear()
            allowed_values_strings = [str(value) for value in self.allowed_values]
            self.widget.addItems(allowed_values_strings)
            self.widget.currentIndexChanged.connect(self.set_from_widget)
        # set value again
        if self.get() not in self.allowed_values:
            print(self.allowed_values)
            self.set(list(self.allowed_values)[0])
        else:
            self.set(self.get())

    def set_widget(self):
        allowed_values_strings = [str(value) for value in self.allowed_values]
        index = allowed_values_strings.index(str(self.get()))
        self.widget.setCurrentIndex(index)

    def set(self, value):
        value = self.data_type(value)
        super().set(value)

    def set_from_widget(self):
        # needs to be defined method so we can connect and disconnect
        self.set(self.widget.currentText())

    def give_control(self, control_widget):
        self.widget = control_widget
        # fill out items
        allowed_values_strings = [str(value) for value in self.allowed_values]
        self.widget.addItems(allowed_values_strings)
        if self.get() is not None:
            self.widget.setCurrentIndex(allowed_values_strings.index(str(self.get())))
        # connect signals and slots
        self.updated.connect(self.set_widget)
        self.widget.currentIndexChanged.connect(self.set_from_widget)
        self.widget.setToolTip(self.tool_tip)
        self.widget.setDisabled(self.disabled)
        self.has_widget = True
