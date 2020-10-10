import pkg_resources
from PyQt5 import uic  # type: ignore
from PyQt5.QtWidgets import QMainWindow, QWidget  # type: ignore
from kryptal.gui.controller.CreateFilesystemController import CreateFilesystemController
from kryptal.gui.view.dialogs.AboutDialog import AboutDialog
from kryptal.model.Filesystems import Filesystems
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from kryptal.services.FilesystemCreatorService import FilesystemCreatorService
from kryptal.services.FilesystemMountService import FilesystemMountService
from kryptal.utils import Paths
from kryptal.gui.view.utils.AsyncSlot import async_slot
from kryptal.gui.controller.MountFilesystemController import MountFilesystemController
from kryptal.gui.controller.RemoveFilesystemController import RemoveFilesystemController
from typing_extensions import Final, final
from kryptal.gui.TrayIcon import TrayIcon


@final
class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        uipath = pkg_resources.resource_filename(__name__, "mainwindow.ui")
        uic.loadUi(uipath, self)

        self.trayIcon = TrayIcon(self)
        self.trayIcon.onExit.connect(self.onExitButtonClick)
        self.trayIcon.show()

        self.createFilesystemButton.clicked.connect(
            self.onCreateFilesystemButtonClick)
        self.aboutButton.clicked.connect(self.onAboutButtonClick)

        self._plugins: Final = KryptalPlugins()

        self._filesystemModel: Final = Filesystems(
            Paths.filesystems_state_file())

        # TODO Pass services in as dependencies?
        self._mountService: Final = FilesystemMountService(self._plugins)
        self._createService: Final = FilesystemCreatorService(
            self._plugins, self._filesystemModel)

        self.fileSystemList.init(self._filesystemModel, MountFilesystemController(
            self._mountService), RemoveFilesystemController(self._filesystemModel, self._mountService, self))

    @async_slot
    async def onCreateFilesystemButtonClick(self, checked: bool) -> None:
        await CreateFilesystemController(self._createService).create()

    @async_slot
    async def onAboutButtonClick(self, checked: bool) -> None:
        await AboutDialog(self._plugins).asyncExec()

    @async_slot
    async def onExitButtonClick(self) -> None:
        self.close()
