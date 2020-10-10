from typing import Optional
from functools import partial
from PyQt5.QtGui import QPalette  # type: ignore
from PyQt5.QtWidgets import QWidget, QFrame, QScrollArea, QVBoxLayout  # type: ignore
from kryptal.gui.view.widgets.FileSystemListItem import FileSystemListItem
from kryptal.model.Filesystem import Filesystem
from kryptal.model.Filesystems import Filesystems
from kryptal.gui.controller.MountFilesystemController import MountFilesystemController
from kryptal.gui.controller.RemoveFilesystemController import RemoveFilesystemController
from kryptal.gui.view.utils.AsyncSlot import async_slot
from typing_extensions import Final, final


@final
class FileSystemList(QScrollArea):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setBackgroundRole(QPalette.Base)
        self.setWidgetResizable(True)
        self.setWidget(QFrame())
        self._layout: Final = QVBoxLayout(self.widget())
        self._updatesDisabled = False
        self._model: Optional[Filesystems] = None
        self._mountController: Optional[MountFilesystemController] = None
        self._update()

    def init(self, model: Filesystems, mountController: MountFilesystemController, removeController: RemoveFilesystemController) -> None:
        self._model = model
        self._model.addChangeHandler(self._update)
        self._mountController = mountController
        self._removeController = removeController
        self._update()

    def _update(self) -> None:
        if not self._updatesDisabled:
            self._clear()
            self._buildList()

    def _buildList(self) -> None:
        if self._model is not None:
            for fs in self._model.filesystems().values():
                self._addListItem(fs)
            self._layout.addStretch()

    def _clear(self) -> None:
        while self._layout.count() > 0:
            widget = self._layout.takeAt(0).widget()
            if widget is not None:
                if isinstance(widget, FileSystemListItem):
                    widget.beforeDestroy()
                widget.deleteLater()

    def _addListItem(self, fs: Filesystem) -> None:
        assert self._mountController is not None
        widget = FileSystemListItem(fs, self._mountController, self)
        widget.onPlaintextDirChanged.connect(
            partial(self._onPlaintextDirChanged, fs.id, widget))
        widget.onRemove.connect(partial(self._onRemove, fs.id))
        self._layout.addWidget(widget)
        self._layout.addWidget(self._horizontalLine())

    def _onPlaintextDirChanged(self, id: int, widget: FileSystemListItem) -> None:
        self._updatesDisabled = True
        assert self._model is not None
        self._model.setPlaintextDirectory(id, widget.plaintextDir())
        self._updatesDisabled = False

    @async_slot
    async def _onRemove(self, id: int) -> None:
        await self._removeController.remove(id=id)

    def _horizontalLine(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setStyleSheet("color: lightgray;")
        return frame
