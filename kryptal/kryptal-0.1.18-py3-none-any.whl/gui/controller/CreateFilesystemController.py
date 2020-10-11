import os
from PyQt5.QtWidgets import QMessageBox  # type: ignore
from kryptal.gui.controller.CreateDirectoryYesNoController import CreateDirectoryYesNoController
from kryptal.gui.view.dialogs.CreateFilesystemDialog import CreateFilesystemDialog, FsTypeEntry
from kryptal.pluginmanager.IFilesystem import FilesystemException
from kryptal.services.FilesystemCreatorService import FilesystemCreatorService
from typing_extensions import Final, final
from typing import List


def _get_supported_fs_type_entries(filesystemCreatorService: FilesystemCreatorService) -> List[FsTypeEntry]:
    fs_types = []
    for fs_type in filesystemCreatorService.list_supported_filesystem_types():
        if fs_type == "CryFS":
            fs_types.append(FsTypeEntry(
                fs_type="CryFS",
                comment="recommended",
            ))
        else:
            fs_types.append(FsTypeEntry(
                fs_type="EncFS",
                comment="insecure",
            ))
    fs_types.sort(key=lambda x: 0 if x.fs_type == "CryFS" else 1)
    return fs_types


@final
class CreateFilesystemController:
    def __init__(self, filesystemCreatorService: FilesystemCreatorService):
        self._filesystemCreatorService: Final = filesystemCreatorService
        self._dlg: Final = CreateFilesystemDialog()
        fs_types = _get_supported_fs_type_entries(filesystemCreatorService)
        self._dlg.setSupportedFilesystemTypes(
            fs_types)
        self._dlg.setAcceptHandler(self._acceptHandler)

    async def create(self) -> None:
        await self._dlg.asyncExec()

    async def _acceptHandler(self, name: str, ciphertextDir: str, plaintextDir: str, password1: str, password2: str, fsType: FsTypeEntry) -> bool:
        if not self._validatePasswords(password1, password2):
            return False

        if not self._validateDirExists('ciphertext directory', ciphertextDir):
            return False

        if not self._validateDirExists('plaintext directory', plaintextDir):
            return False

        return await self._createFilesystem(name=name, fstype=fsType.fs_type, ciphertextDir=ciphertextDir, plaintextDir=plaintextDir, password=password1)

    def _validatePasswords(self, password1: str, password2: str) -> bool:
        if password1 == password2:
            return True
        QMessageBox.warning(self._dlg, "Passwords don't match",
                            "Passwords don't match. Please enter the same password in both fields.")
        self._dlg.clearPasswordFields()
        return False

    def _validateDirExists(self, name: str, path: str) -> bool:
        if os.path.isdir(path):
            return True
        return CreateDirectoryYesNoController(self._dlg).askYesNoAndCreateDir(name, path)

    async def _createFilesystem(self, name: str, fstype: str, ciphertextDir: str, plaintextDir: str, password: str) -> bool:
        try:
            await self._filesystemCreatorService.create_and_mount(name=name, fstype=fstype, ciphertextDirectory=ciphertextDir, plaintextDirectory=plaintextDir, password=password.encode(encoding='UTF-8'))
            return True
        except FilesystemException as e:
            QMessageBox.critical(
                self._dlg, "Error creating file system", e.message())
            return False
