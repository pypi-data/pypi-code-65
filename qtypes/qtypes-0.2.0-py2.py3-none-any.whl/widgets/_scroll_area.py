__all__ = ["ScrollArea"]


from qtpy import QtCore, QtWidgets


class ScrollArea(QtWidgets.QScrollArea):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFixedWidth(
            300 + self.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent) + 10
        )
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.child = QtWidgets.QWidget()
        self.child.setFixedWidth(
            300 + self.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent) + 10
        )
        self.child.setLayout(QtWidgets.QVBoxLayout())
        self.child.layout().setContentsMargins(0, 0, 0, 0)
        self.child.layout().addStretch(1)
        self.setWidget(self.child)

    def add_widget(self, widget):
        self.child.layout().insertWidget(self.child.layout().count() - 1, widget)
