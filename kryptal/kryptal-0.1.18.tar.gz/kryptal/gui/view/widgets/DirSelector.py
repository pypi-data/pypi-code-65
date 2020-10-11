from PyQt5.QtCore import pyqtSignal  # type: ignore
from PyQt5.QtWidgets import QCompleter, QWidget, QFileDialog  # type: ignore
from PyQt5 import uic  # type: ignore
import pkg_resources
from kryptal.gui.view.utils import DirCompleter
from os.path import expanduser
from typing_extensions import final


_homedir = expanduser("~")


@final
class DirSelector(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        uipath = pkg_resources.resource_filename(__name__, "dirselector.ui")
        uic.loadUi(uipath, self)

        self.browseButton.clicked.connect(self._onBrowseButtonClicked)
        self.setFocusProxy(self.directoryEdit)

        completer = DirCompleter.get(parent=self.directoryEdit)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.directoryEdit.setCompleter(completer)

        self.directoryEdit.editingFinished.connect(self.directoryChanged.emit)

    def setDirectory(self, value: str) -> None:
        self.directoryEdit.setText(value)

    def directory(self) -> str:
        txt: str = self.directoryEdit.text()
        return txt

    directoryChanged = pyqtSignal()

    def _onBrowseButtonClicked(self) -> None:
        fileDlg = QFileDialog(self)
        fileDlg.setFileMode(QFileDialog.Directory)
        fileDlg.setOption(QFileDialog.ShowDirsOnly)
        if self.directoryEdit.text() == "":
            fileDlg.setDirectory(_homedir)
        else:
            fileDlg.setDirectory(self.directoryEdit.text())

        if fileDlg.exec_():
            self.directoryEdit.setText(fileDlg.selectedFiles()[0])
            self.directoryChanged.emit()
