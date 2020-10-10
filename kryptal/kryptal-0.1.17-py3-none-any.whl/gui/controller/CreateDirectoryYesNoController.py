import os
from PyQt5.QtWidgets import QMessageBox, QWidget  # type: ignore
from typing_extensions import Final, final


@final
class CreateDirectoryYesNoController:
    def __init__(self, parent: QWidget):
        self._parent: Final = parent

    def askYesNoAndCreateDir(self, name: str, path: str) -> bool:
        if self._askYesNo("Create %s?" % name, "The %s doesn't exist. Do you want to create it?" % name):
            return self._createDirectory(name, path)
        return False

    def _createDirectory(self, name: str, path: str) -> bool:
        try:
            os.makedirs(path)
            return True
        except PermissionError:
            QMessageBox.warning(self._parent, "Error creating %s" % name,
                                "Couldn't create %s because of missing permissions." % name)
            return False
        except:
            QMessageBox.warning(self._parent, "Error creating %s" %
                                name, "Couldn't create %s." % name)
            return False

    def _askYesNo(self, title: str, question: str) -> bool:
        res: bool = QMessageBox.Yes == QMessageBox.question(self._parent, title, question, QMessageBox.Yes | QMessageBox.No,
                                                            QMessageBox.Yes)
        return res
