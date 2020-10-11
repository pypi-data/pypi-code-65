from typing import List, Callable, Dict
import copy
from kryptal.model.Filesystem import Filesystem
from kryptal.model.FilesystemStateFileRef import FilesystemsStateFileRef
from typing_extensions import Final, final


@final
class Filesystems:
    def __init__(self, stateFilePath: str):
        self._stateFile: Final = FilesystemsStateFileRef(stateFilePath)
        self._filesystems: Final = self._loadState()
        self._changeHandlers: List[Callable[[], None]] = []
        self.addChangeHandler(self._saveState)

    def add(self, name: str, fstype: str, ciphertextDirectory: str, plaintextDirectory: str) -> Filesystem:
        new_id = self._new_id()
        filesystem = Filesystem(id=new_id, name=name, fstype=fstype,
                                ciphertextDirectory=ciphertextDirectory, plaintextDirectory=plaintextDirectory)
        self._filesystems[new_id] = filesystem
        self._callChangeHandlers()
        return filesystem

    # TODO Test
    def remove(self, id: int) -> None:
        del self._filesystems[id]
        self._callChangeHandlers()

    def filesystems(self) -> Dict[int, Filesystem]:
        # Copy to make sure nobody modifies our internal data
        return copy.deepcopy(self._filesystems)

    def addChangeHandler(self, changeHandler: Callable[[], None]) -> None:
        self._changeHandlers.append(changeHandler)

    def setPlaintextDirectory(self, id: int, plaintextDir: str) -> Filesystem:
        self._filesystems[id] = self._filesystems[id]._replace(
            plaintextDirectory=plaintextDir)
        self._callChangeHandlers()
        return self._filesystems[id]

    def _new_id(self) -> int:
        used_ids = self._filesystems.keys()
        if len(used_ids) == 0:
            max_id = -1
        else:
            max_id = max(used_ids)
        return max_id + 1

    def _callChangeHandlers(self) -> None:
        for handler in self._changeHandlers:
            handler()

    def _loadState(self) -> Dict[int, Filesystem]:
        filesystems = self._stateFile.load()
        filesystems_map = {fs.id: fs for fs in filesystems}
        # Assert there haven't been any duplicate IDs
        assert len(filesystems) == len(filesystems_map)
        return filesystems_map

    def _saveState(self) -> None:
        self._stateFile.save(self._filesystems.values())
