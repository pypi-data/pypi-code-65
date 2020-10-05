__all__ = ["Line"]


import os
import toml

from qtpy import QtWidgets


here = os.path.abspath(os.path.dirname(__file__))

colors = toml.load(os.path.join(here, "colors.toml"))["night"]


class Line(QtWidgets.QFrame):
    """
    direction: 'V' or 'H'
    """

    def __init__(self, direction):
        super().__init__()
        if direction == "V":
            self.setFrameShape(QtWidgets.QFrame.VLine)
        else:
            self.setFrameShape(QtWidgets.QFrame.HLine)
        StyleSheet = "QFrame{border: 2px solid custom_color; border-radius: 0px; padding: 0px;}".replace(
            "custom_color", colors["foreground"]
        )
        self.setStyleSheet(StyleSheet)
