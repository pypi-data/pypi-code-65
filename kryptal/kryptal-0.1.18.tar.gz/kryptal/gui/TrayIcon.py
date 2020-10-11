
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QWidget, QAction  # type: ignore
from PyQt5.QtGui import QIcon  # type: ignore
from PyQt5.QtCore import pyqtSignal  # type: ignore
from kryptal.gui.view.utils.AsyncSlot import async_slot
from kryptal.gui.view.icons import Icons


class TrayIcon(QSystemTrayIcon):
    onExit = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        super().__init__(_icon(), parent)
        self.menu = QMenu(parent=parent)
        exitAction = self.menu.addAction("Exit")
        exitAction.triggered.connect(self.onExit.emit)
        self.setContextMenu(self.menu)


def _icon() -> QIcon:
    return QIcon(Icons.get_path("logo.png"))
