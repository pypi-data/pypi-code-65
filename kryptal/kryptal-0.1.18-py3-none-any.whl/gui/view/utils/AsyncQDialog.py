from PyQt5.QtWidgets import QDialog, QWidget, QMessageBox  # type: ignore
from PyQt5.Qt import Qt  # type: ignore
import asyncio
from asyncio.futures import Future
from typing import Optional, List
from typing_extensions import Final
from enum import Enum
from typing_extensions import final


# TODO Add tests
class AsyncQDialog(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.finished.connect(self._onFinished)
        self._resultFuture: Optional[Future[int]] = None

    async def asyncExec(self) -> int:
        self.setWindowModality(Qt.ApplicationModal)
        self._resultFuture = asyncio.get_event_loop().create_future()
        self.show()
        result = await self._resultFuture
        return result

    def _onFinished(self, result: int) -> None:
        if (self._resultFuture is not None):
            self._resultFuture.set_result(result)


@final
class DialogButton(Enum):
    Yes: Final = 0
    No: Final = 1
    Cancel: Final = 2


# TODO Use AsyncQMessageBox everywhere instead of QMessageBox
# TODO Add tests
@final
class AsyncQMessageBox:
    def __init__(self, parent: QWidget):
        self._dlg = QMessageBox(parent)
        self._resultFuture: Optional[Future[DialogButton]] = None

    async def question(self, title: str, text: str, buttons: List[DialogButton], defaultButton: DialogButton) -> DialogButton:
        self._dlg.setWindowTitle(title)
        self._dlg.setText(text)
        self._dlg.setIcon(QMessageBox.Question)
        self._dlg.setWindowModality(Qt.ApplicationModal)
        self._dlg.setStandardButtons(self._parseButtons(buttons))
        self._dlg.setDefaultButton(self._parseButton(defaultButton))
        self._dlg.finished.connect(self._onFinished)
        self._resultFuture = asyncio.get_event_loop().create_future()
        self._dlg.show()
        result = await self._resultFuture
        return result

    def _parseButton(self, button: DialogButton) -> QMessageBox.StandardButton:
        return {
            DialogButton.Yes: QMessageBox.Yes,
            DialogButton.No: QMessageBox.No,
            DialogButton.Cancel: QMessageBox.Cancel
        }[button]

    def _parseButtons(self, buttons: List[DialogButton]) -> QMessageBox.StandardButtons:
        result = 0
        for button in buttons:
            result = result | self._parseButton(button)
        return result

    def _onFinished(self, result: int) -> None:
        if (self._resultFuture is not None):
            res = {
                QMessageBox.Yes: DialogButton.Yes,
                QMessageBox.No: DialogButton.No,
                QMessageBox.Cancel: DialogButton.Cancel
            }[result]
            self._resultFuture.set_result(res)
