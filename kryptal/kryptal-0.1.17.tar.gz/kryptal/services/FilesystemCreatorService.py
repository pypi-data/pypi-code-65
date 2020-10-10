from kryptal.model.Filesystems import Filesystems
from kryptal.model.Filesystem import Filesystem
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from typing_extensions import Final, final
from typing import Sequence


@final
class FilesystemCreatorService:
    def __init__(self, kryptalPlugins: KryptalPlugins, filesystemModel: Filesystems):
        self._kryptalPlugins: Final = kryptalPlugins
        self._filesystemModel: Final = filesystemModel

    def list_supported_filesystem_types(self) -> Sequence[str]:
        return list(self._kryptalPlugins.filesystems().keys())

    async def create_and_mount(self, name: str, fstype: str, ciphertextDirectory: str, plaintextDirectory: str, password: bytes) -> None:
        await self._kryptalPlugins.filesystems()[fstype].create_and_mount(ciphertextDir=ciphertextDirectory, plaintextDir=plaintextDirectory, password=password)
        self._filesystemModel.add(
            name=name, fstype=fstype, ciphertextDirectory=ciphertextDirectory, plaintextDirectory=plaintextDirectory)
