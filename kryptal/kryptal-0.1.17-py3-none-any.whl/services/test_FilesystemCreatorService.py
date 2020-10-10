from unittest.mock import create_autospec, Mock
from kryptal.model.Filesystems import Filesystems
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from kryptal.services.FilesystemCreatorService import FilesystemCreatorService
from kryptal.testutils.ApplicationHelpers import async_unit
from .DummyFilesystem import DummyFilesystem
import unittest


fs_name = "My name"
fs_fstype = "MyFSType"
fs_ciphertextDirectory = "/my/ciphertext"
fs_plaintextDirectory = "/my/plaintext"
fs_password = "mypassword".encode(encoding="UTF-8")


class test_FilesystemCreatorService(unittest.TestCase):
    @async_unit
    async def test_adds_to_model(self) -> None:
        plugins = Mock(KryptalPlugins())
        fsplugin = Mock(DummyFilesystem())
        plugins.filesystems.return_value = {fs_fstype: fsplugin}
        model = create_autospec(Filesystems)
        service = FilesystemCreatorService(plugins, model)
        await service.create_and_mount(name=fs_name, fstype=fs_fstype, password=fs_password,
                                       ciphertextDirectory=fs_ciphertextDirectory,
                                       plaintextDirectory=fs_plaintextDirectory)
        model.add.assert_called_once_with(
            name=fs_name, fstype=fs_fstype, ciphertextDirectory=fs_ciphertextDirectory, plaintextDirectory=fs_plaintextDirectory)

    @async_unit
    async def test_creates_filesystem(self) -> None:
        plugins = Mock(KryptalPlugins())
        fsplugin = Mock(DummyFilesystem())
        plugins.filesystems.return_value = {
            fs_fstype: fsplugin, "other": Mock(DummyFilesystem())}
        model = create_autospec(Filesystems)
        service = FilesystemCreatorService(plugins, model)
        await service.create_and_mount(name=fs_name, fstype=fs_fstype, password=fs_password,
                                       ciphertextDirectory=fs_ciphertextDirectory,
                                       plaintextDirectory=fs_plaintextDirectory)
        fsplugin.create_and_mount.assert_called_once_with(
            ciphertextDir=fs_ciphertextDirectory, plaintextDir=fs_plaintextDirectory, password=fs_password)
