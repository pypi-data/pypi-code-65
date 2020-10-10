from typing import Callable, Awaitable
import os
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from kryptal.utils.PollProcess import PollProcess
from kryptal.utils.AsyncObservable import ListenerHandle
from typing_extensions import Final, final


@final
class FilesystemMountService:
    def __init__(self, plugins: KryptalPlugins):
        self._plugins: Final = plugins
        self._mountChangeMonitor: Final = PollProcess(
            "findmnt", "--poll", "--first-only")
        self._mountChangeMonitor.start()

    async def mount(self, fstype: str, ciphertextDir: str, plaintextDir: str, password: bytes) -> None:
        plugin = self._plugins.filesystems()[fstype]
        os.makedirs(plaintextDir, exist_ok=True)
        await plugin.mount(ciphertextDir=ciphertextDir, plaintextDir=plaintextDir, password=password)

    async def unmount(self, fstype: str, plaintextDir: str) -> None:
        plugin = self._plugins.filesystems()[fstype]
        await plugin.unmount(plaintextDir=plaintextDir)

    async def is_mounted(self, fstype: str, ciphertextDir: str, plaintextDir: str) -> bool:
        plugin = self._plugins.filesystems()[fstype]
        return await plugin.is_mounted(ciphertextDir=ciphertextDir, plaintextDir=plaintextDir)

    # TODO Test
    def addChangeHandler(self, handler: Callable[[], Awaitable[None]]) -> ListenerHandle:
        return self._mountChangeMonitor.addListener(handler)

    # TODO Test
    def removeChangeHandler(self, handle: ListenerHandle) -> None:
        return self._mountChangeMonitor.removeListener(handle)
