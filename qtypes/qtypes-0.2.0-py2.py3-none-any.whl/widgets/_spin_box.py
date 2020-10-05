from qtpy import QtWidgets


class DoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setFixedHeight(25)

    def wheelEvent(self, *args, **kwargs):
        # overload to disable interaction with mouse wheel
        pass
