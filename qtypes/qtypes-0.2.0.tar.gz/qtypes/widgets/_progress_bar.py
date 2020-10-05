__all__ = ["ProgressBar"]


import os
from qtpy import QtWidgets


class ProgressBar(QtWidgets.QProgressBar):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(55)
        self.setMinimumWidth(600)
        self.setTextVisible(False)
        #
        self._elapsed = QtWidgets.QLabel("00:00:00")
        self._remaining = QtWidgets.QLabel("00:00:00")
        self._message = QtWidgets.QLabel("")
        #
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(self._elapsed)
        self.layout().addStretch(1)
        self.layout().addWidget(self._message)
        self.layout().addStretch(1)
        self.layout().addWidget(self._remaining)
