__all__ = ["Filepath"]


from qtpy import QtCore, QtGui, QtWidgets
from ._base import Base


class Filepath(Base):
    def __init__(
        self, caption="Open", directory=None, options=[], kind="file", *args, **kwargs
    ):
        """
        holds the filepath as a string \n
        Kind one in {'file', 'directory'}
        """
        super().__init__(*args, **kwargs)
        self.qtype = "filepath"
        self.caption = caption
        self.directory = directory
        self.options = options
        self.kind = kind

    def give_control(self, control_widget):
        self.widget = control_widget
        if self.get() is not None:
            self.widget.setText(self.get())
        # connect signals and slots
        self.updated.connect(lambda: self.widget.setText(self.get()))
        self.widget.setToolTip(str(self.get()))
        self.updated.connect(lambda: self.widget.setToolTip(self.get()))
        self.has_widget = True

    def give_button(self, button_widget):
        self.button = button_widget
        self.button.clicked.connect(self.on_load)

    def on_load(self):
        # TODO: better filter handling
        chosen = str(QtWidgets.QFileDialog.getOpenFileName())[0]
        self.set(chosen)

    def get(self):
        return str(super().get())

    def get_saved(self):
        self.updated.emit()

    def save(self, value=None):
        if value is not None:
            self.value.get(value)
