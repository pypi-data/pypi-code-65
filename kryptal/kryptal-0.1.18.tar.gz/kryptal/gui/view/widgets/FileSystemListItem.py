from PyQt5.QtCore import pyqtSignal  # type: ignore
from PyQt5.QtGui import QIcon, QPixmap  # type: ignore
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QMessageBox  # type: ignore
from PyQt5 import uic  # type: ignore
import pkg_resources
from kryptal.gui.view.icons import Icons
from kryptal.gui.view.utils.AsyncSlot import async_slot
from kryptal.model.Filesystem import Filesystem
from kryptal.pluginmanager.IFilesystem import FilesystemException
from kryptal.gui.controller.MountFilesystemController import MountFilesystemController
import kryptal.gui.TaskManager as TaskManager
from typing_extensions import Final, final


# TODO Test: mounting, unmounting
# TODO Test view updates when findmnt poll notices a mount change
@final
class FileSystemListItem(QWidget):
    def __init__(self, filesystem: Filesystem, mountController: MountFilesystemController, parent: QWidget = None):
        super().__init__(parent)

        uipath = pkg_resources.resource_filename(
            __name__, "filesystemlistitem.ui")
        uic.loadUi(uipath, self)
        self.nameLabel.setText(filesystem.name)
        self.fstypeLabel.setText(filesystem.fstype)
        self.plaintextDirSelector.setDirectory(filesystem.plaintextDirectory)
        self.ciphertextDirLabel.setText(filesystem.ciphertextDirectory)

        self.plaintextDirSelector.directoryChanged.connect(
            self._plaintextDirChanged)

        self.icon.setPixmap(QPixmap(Icons.get_path("drive-harddisk.svg")))
        self.detailsButton.setIcon(QIcon(Icons.get_path("gear.svg")))
        self.detailsButton.clicked.connect(self._onDetailsButtonClick)
        self.detailsFrame.setVisible(False)

        self._filesystem = filesystem
        self._mountController: Final = mountController

        self._changeHandlerHandle: Final = self._mountController.addChangeHandler(
            self._updateMountState)
        self._valid = True
        TaskManager.create_task(self._updateMountState())

        self.mountButton.clicked.connect(self._onMountButtonClick)
        self.removeButton.clicked.connect(self.onRemove.emit)

    def beforeDestroy(self) -> None:
        self._valid = False
        self._mountController.removeChangeHandler(self._changeHandlerHandle)

    onPlaintextDirChanged = pyqtSignal()
    onRemove = pyqtSignal()

    def plaintextDir(self) -> str:
        dir: str = self.plaintextDirSelector.directory()
        return dir

    # TODO Test
    def ciphertextDir(self) -> str:
        dir: str = self.ciphertextDirLabel.text()
        return dir

    # TODO Test
    def fstype(self) -> str:
        fstype: str = self.fstypeLabel.text()
        return fstype

    def mouseReleaseEvent(self, evt: QMouseEvent) -> None:
        self.detailsButton.setChecked(not self.detailsButton.isChecked())
        self._onDetailsButtonClick()

    async def _updateMountState(self) -> None:
        is_mounted = await self._mountController.is_mounted(fstype=self._filesystem.fstype,
                                                            ciphertextDir=self._filesystem.ciphertextDirectory, plaintextDir=self._filesystem.plaintextDirectory)
        # It's possible that the object was already destroyed, for example when
        # multiple entries are added in-sequence to the model and each immediately
        # calls onChangeHandlers, causing the FileSystemList to rebuild all FileSystemListItems,
        # before there is a change to get back to _updateMountState here.
        # Let's just exit if this item is already dead.
        if not self._valid:
            return

        self.mountButton.setChecked(is_mounted)

    def _onDetailsButtonClick(self) -> None:
        self.detailsFrame.setVisible(self.detailsButton.isChecked())

    def _plaintextDirChanged(self) -> None:
        self._filesystem = self._filesystem._replace(
            plaintextDirectory=self.plaintextDirSelector.directory())
        self.onPlaintextDirChanged.emit()

    # TODO Test:
    # - FilesystemException show QMessageBox
    # - unknown exceptions are not silently ignored
    # - on unknown exceptions, spinner is still stopped
    @async_slot
    async def _onMountButtonClick(self, checked: bool) -> None:
        self.mountButton.startSpinner()
        try:
            if self.mountButton.isChecked():
                await self._mount()
            else:
                await self._unmount()
        finally:
            await self._updateMountState()
            self.mountButton.stopSpinner()

    async def _mount(self) -> None:
        try:
            await self._mountController.mount(fstype=self._filesystem.fstype, ciphertextDir=self._filesystem.ciphertextDirectory, plaintextDir=self._filesystem.plaintextDirectory)
        except FilesystemException as e:
            QMessageBox.critical(None, "Error mounting file system", str(e))

    async def _unmount(self) -> None:
        try:
            await self._mountController.unmount(fstype=self._filesystem.fstype,
                                                plaintextDir=self._filesystem.plaintextDirectory)
        except FilesystemException as e:
            QMessageBox.critical(None, "Error unmounting file system", str(e))
