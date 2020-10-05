from qtpy import QtWidgets, QtCore


class ExpandingWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.setMinimumHeight(0)
        self.setMinimumWidth(0)
        self.layout().setStretchFactor(self, 1)

    def sizeHint(self):
        return QtCore.QSize(16777215, 16777215)

    def add_to_layout(self, layout):
        layout.addWidget(self)
        layout.setStretchFactor(self, 16777215)
