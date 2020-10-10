from kryptal.services.FilesystemMountService import FilesystemMountService
from PyQt5.QtWidgets import QWidget, QProgressDialog  # type: ignore
from PyQt5.QtCore import Qt  # type: ignore
from kryptal.model.Filesystems import Filesystems
from kryptal.gui.view.utils.AsyncQDialog import AsyncQMessageBox, DialogButton
import asyncio
from functools import partial
from typing import Callable, cast, Optional
from types import TracebackType
from kryptal.utils.RmTree import rmtree
import time
from typing_extensions import Final, final


@final
class _ProgressDialog:
    def __init__(self, text: str, loop: asyncio.AbstractEventLoop, parent: QWidget):
        self._loop: Final = loop
        self._dlg: Final = QProgressDialog(
            text, None, 0, 1000, parent, Qt.FramelessWindowHint)
        self._dlg.setAutoClose(False)
        self._dlg.setAutoReset(False)
        self._dlg.setWindowModality(Qt.ApplicationModal)

    def __enter__(self) -> "_ProgressDialog":
        self._lastProgressUpdate: float = 0
        self._dlg.show()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception],
                 exc_tb: Optional[TracebackType]) -> None:
        self._dlg.close()

    def setProgress(self, progress: float) -> None:
        curTime = time.time()
        if (curTime > self._lastProgressUpdate + 0.05):
            self._loop.call_soon_threadsafe(
                partial(self._dlg.setValue, 1000 * progress))
            self._lastProgressUpdate = curTime


# TODO Test
@final
class RemoveFilesystemController:
    def __init__(self, filesystemModel: Filesystems, mountService: FilesystemMountService, parent: QWidget):
        self._filesystemModel: Final = filesystemModel
        self._mountService: Final = mountService
        self._parent: Final = parent

    async def remove(self, id: int) -> None:
        fs = self._filesystemModel.filesystems()[id]
        if await self._mountService.is_mounted(fstype=fs.fstype, ciphertextDir=fs.ciphertextDirectory, plaintextDir=fs.plaintextDirectory):
            if not await self._askUnmount(fstype=fs.fstype, plaintextDir=fs.plaintextDirectory):
                return

        removeContents = await self._askYesNoCancel("Remove contents?", "Do you also want to remove the file system contents? Warning: This irreversably loses the data stored in them.")
        if removeContents == DialogButton.Cancel:
            return

        if removeContents == DialogButton.Yes:
            loop = asyncio.get_event_loop()
            with _ProgressDialog("Removing file system contents", loop, self._parent) as progressDialog:
                remover = cast(Callable[..., None], partial(
                    rmtree, fs.ciphertextDirectory, progressDialog.setProgress))
                await loop.run_in_executor(None, remover)

        self._filesystemModel.remove(id)

    async def _askUnmount(self, fstype: str, plaintextDir: str) -> bool:
        shouldUnmount = await self._askYesNo("Unmount file system?", "The file system is currently mounted. Do you want to unmount it?")
        if shouldUnmount:
            await self._mountService.unmount(fstype=fstype, plaintextDir=plaintextDir)
        return shouldUnmount

    async def _askYesNo(self, title: str, question: str) -> bool:
        res: bool = DialogButton.Yes == await AsyncQMessageBox(self._parent).question(title, question, [DialogButton.Yes, DialogButton.No], DialogButton.Yes)
        return res

    async def _askYesNoCancel(self, title: str, question: str) -> DialogButton:
        return await AsyncQMessageBox(self._parent).question(title, question, [DialogButton.Yes, DialogButton.No, DialogButton.Cancel], DialogButton.Yes)
