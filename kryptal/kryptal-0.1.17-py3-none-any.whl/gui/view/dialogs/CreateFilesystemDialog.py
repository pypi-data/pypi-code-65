from typing import List, Callable, Awaitable, Any, Optional, Coroutine
import pkg_resources
from PyQt5 import uic  # type: ignore
from PyQt5.QtWidgets import QWidget  # type: ignore
from kryptal.gui.view.utils.PasswordsMatchPolicy import display
from kryptal.gui.view.utils.AsyncSlot import async_slot
from kryptal.gui.view.utils.AsyncQDialog import AsyncQDialog
from typing_extensions import final
from typing import List, Optional
from dataclasses import dataclass


async def _defaultAcceptHandler(*args: Any, **kwargs: Any) -> bool:
    return True


@dataclass(frozen=True)
class FsTypeEntry:
    fs_type: str
    comment: Optional[str]


@final
class CreateFilesystemDialog(AsyncQDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        uipath = pkg_resources.resource_filename(
            __name__, "createfilesystemdialog.ui")
        uic.loadUi(uipath, self)

        display(self.passwordsMatchIndicator).whenPasswordsDontMatch([
            self.password1Edit, self.password2Edit
        ])

        self._acceptHandler = _defaultAcceptHandler

        self._fs_types: List[FsTypeEntry] = []

        # Setting tab order in QtDesigner doesn't work for nested widgets, do it manually.
        # See also: http://stackoverflow.com/questions/18641879/how-can-i-set-qt-tab-order-for-a-form-with-a-composite-widget
        #           https://bugreports.qt.io/browse/QTBUG-10907
        self._setTabOrder([
            self.nameLabel,
            self.ciphertextDirSelector.directoryEdit,
            self.ciphertextDirSelector.browseButton,
            self.plaintextDirSelector.directoryEdit,
            self.plaintextDirSelector.browseButton,
            self.password1Edit,
            self.password2Edit,
            self.filesystemTypeComboBox,
            self.dialogButtons
        ])

    def setSupportedFilesystemTypes(self, fs_types: List[FsTypeEntry]) -> None:
        self._fs_types = fs_types
        self.filesystemTypeComboBox.clear()
        for fs_type in self._fs_types:
            if fs_type.comment is None:
                self.filesystemTypeComboBox.addItem(fs_type.fs_type)
            else:
                self.filesystemTypeComboBox.addItem(
                    "{} ({})".format(fs_type.fs_type, fs_type.comment))

    def _setTabOrder(self, order: List[QWidget]) -> None:
        for i in range(1, len(order)):
            self.setTabOrder(order[i-1], order[i])

    def setAcceptHandler(self, acceptHandler: Callable[..., Coroutine[None, None, bool]]) -> None:
        self._acceptHandler = acceptHandler

    def clearPasswordFields(self) -> None:
        self.password1Edit.setText("")
        self.password2Edit.setText("")
        self.password1Edit.setFocus()

    def _startProgressAnimation(self) -> None:
        self.progressLabel.start()

    def _stopProgressAnimation(self) -> None:
        self.progressLabel.stop()

    @async_slot
    async def accept(self) -> None:
        try:
            self.setEnabled(False)
            self._startProgressAnimation()
            if await self._acceptHandler(
                name=self.nameEdit.text(),
                ciphertextDir=self.ciphertextDirSelector.directory(),
                plaintextDir=self.plaintextDirSelector.directory(),
                password1=self.password1Edit.text(),
                password2=self.password2Edit.text(),
                fsType=self._fs_types[self.filesystemTypeComboBox.currentIndex()],
            ):
                super(CreateFilesystemDialog, self).accept()
        finally:
            self._stopProgressAnimation()
            self.setEnabled(True)
