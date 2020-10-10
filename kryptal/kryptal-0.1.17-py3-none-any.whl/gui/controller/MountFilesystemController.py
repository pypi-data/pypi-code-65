from typing import Callable, Awaitable
from kryptal.services.FilesystemMountService import FilesystemMountService
from kryptal.utils.AsyncObservable import ListenerHandle
from PyQt5.QtWidgets import QInputDialog, QLineEdit  # type: ignore
from typing_extensions import Final, final


# TODO Test
@final
class MountFilesystemController:
    def __init__(self, mountService: FilesystemMountService):
        self._mountService: Final = mountService

    async def mount(self, fstype: str, ciphertextDir: str, plaintextDir: str) -> None:
        password, accepted = QInputDialog.getText(
            None, "Please enter password", "Password: ", QLineEdit.Password)
        if accepted:
            return await self._mountService.mount(fstype=fstype, ciphertextDir=ciphertextDir, plaintextDir=plaintextDir, password=password.encode(encoding="UTF-8"))

    async def unmount(self, fstype: str, plaintextDir: str) -> None:
        return await self._mountService.unmount(fstype=fstype, plaintextDir=plaintextDir)

    async def is_mounted(self, fstype: str, ciphertextDir: str, plaintextDir: str) -> bool:
        return await self._mountService.is_mounted(fstype=fstype, ciphertextDir=ciphertextDir, plaintextDir=plaintextDir)

    def addChangeHandler(self, handler: Callable[[], Awaitable[None]]) -> ListenerHandle:
        return self._mountService.addChangeHandler(handler)

    def removeChangeHandler(self, handle: ListenerHandle) -> None:
        return self._mountService.removeChangeHandler(handle)
