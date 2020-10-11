from typing import NamedTuple, List, Optional

from abc import ABCMeta, abstractmethod
from yapsy.IPlugin import IPlugin
from asyncio import Task
from typing_extensions import Final


MountedFilesystem = NamedTuple('MountedFilesystem', [
    ('ciphertextDirectory', Optional[str]),
    ('plaintextDirectory', str)
])


class IFilesystem(IPlugin, metaclass=ABCMeta):
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def create_and_mount(self, ciphertextDir: str, plaintextDir: str, password: bytes) -> None: ...

    @abstractmethod
    async def mount(self, ciphertextDir: str, plaintextDir: str, password: bytes) -> None: ...

    @abstractmethod
    async def unmount(self, plaintextDir: str) -> None: ...

    @abstractmethod
    async def mounted_filesystems(self) -> List[MountedFilesystem]: ...

    async def is_mounted(self, ciphertextDir: str, plaintextDir: str) -> bool:
        for fs in await self.mounted_filesystems():
            if fs.plaintextDirectory == plaintextDir and (fs.ciphertextDirectory is None or fs.ciphertextDirectory == ciphertextDir):
                return True
        return False


class FilesystemException(Exception):
    def __init__(self, message: str) -> None:
        self._message: Final = message

    def message(self) -> str:
        return self._message
