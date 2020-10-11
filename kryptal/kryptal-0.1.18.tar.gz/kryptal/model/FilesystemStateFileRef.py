from typing import List, Any, Dict, Iterable
from kryptal.model.ConfigFileRef import ConfigFileRef
from kryptal.model.Filesystem import Filesystem
from typing_extensions import Final, final


_id = 0


@final
class FilesystemsStateFileRef:
    def __init__(self, path: str):
        self._file: Final = ConfigFileRef(path)

    def save(self, filesystems: Iterable[Filesystem]) -> None:
        self._file.save({
            'filesystems': [self._serializeFilesystem(fs) for fs in filesystems]
        })

    def load(self) -> List[Filesystem]:
        try:
            fileobj = self._file.load()
            return [self._deserializeFilesystem(fs) for fs in fileobj['filesystems']]
        except FileNotFoundError:
            return []

    def _serializeFilesystem(self, fs: Filesystem) -> Dict[str, Any]:
        return {
            'id': fs.id,
            'name': fs.name,
            'fstype': fs.fstype,
            'ciphertextDirectory': fs.ciphertextDirectory,
            'plaintextDirectory': fs.plaintextDirectory
        }

    def _deserializeFilesystem(self, serialized: Dict[str, Any]) -> Filesystem:
        return Filesystem(
            id=serialized['id'],
            name=serialized['name'],
            fstype=serialized['fstype'],
            ciphertextDirectory=serialized['ciphertextDirectory'],
            plaintextDirectory=serialized['plaintextDirectory']
        )
