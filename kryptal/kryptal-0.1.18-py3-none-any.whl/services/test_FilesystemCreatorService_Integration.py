import unittest
import os
import tempfile
from kryptal.model.Filesystems import Filesystems
from kryptal.model.Filesystem import Filesystem
from kryptal.pluginmanager.IFilesystem import IFilesystem, MountedFilesystem
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from kryptal.services.FilesystemCreatorService import FilesystemCreatorService
from yapsy.PluginInfo import PluginInfo
from kryptal.testutils.ApplicationHelpers import async_unit
from unittest.mock import create_autospec, Mock
from .DummyFilesystem import DummyFilesystem


fs_name = "My name"
fs_fstype = "MyFSType"
fs_ciphertextDirectory = "/my/ciphertext"
fs_plaintextDirectory = "/my/plaintext"
fs_password = "mypassword".encode(encoding="UTF-8")


def assert_fs_equals(testcase: unittest.TestCase, fs: Filesystem, name: str, fstype: str, ciphertextDirectory: str, plaintextDirectory: str) -> None:
    testcase.assertEqual(name, fs.name)
    testcase.assertEqual(fstype, fs.fstype)
    testcase.assertEqual(ciphertextDirectory, fs.ciphertextDirectory)
    testcase.assertEqual(plaintextDirectory, fs.plaintextDirectory)


class test_FilesystemCreatorService_Integration(unittest.TestCase):
    def setUp(self) -> None:
        self.plugins = KryptalPlugins()
        self.mockPlugin = self._createMockPlugin()
        self._addMockPlugin(self.plugins, self.mockPlugin)
        self._stateTempDir = tempfile.TemporaryDirectory()
        self.model = Filesystems(os.path.join(
            self._stateTempDir.name, "filesystems.yaml"))
        self.service = FilesystemCreatorService(self.plugins, self.model)

    def tearDown(self) -> None:
        self._stateTempDir.cleanup()

    def _createMockPlugin(self) -> Mock:
        fsPluginMock = Mock(DummyFilesystem())
        fsPluginMock.name.return_value = fs_fstype
        return fsPluginMock

    def _addMockPlugin(self, plugins: KryptalPlugins, plugin: IFilesystem) -> None:
        fsPluginInfoMock = create_autospec(PluginInfo)
        fsPluginInfoMock.plugin_object = plugin
        fsPluginInfoMock.name.return_value = fs_fstype
        plugins._filesystemPlugins._manager.appendPluginToCategory(
            fsPluginInfoMock, "Filesystem")

    @async_unit
    async def test_adds_to_model(self) -> None:
        await self.service.create_and_mount(name=fs_name, fstype=fs_fstype, password=fs_password,
                                            ciphertextDirectory=fs_ciphertextDirectory,
                                            plaintextDirectory=fs_plaintextDirectory)
        self.assertEqual(1, len(self.model.filesystems()))
        assert_fs_equals(self, list(self.model.filesystems().values())[
                         0], name=fs_name, fstype=fs_fstype, ciphertextDirectory=fs_ciphertextDirectory, plaintextDirectory=fs_plaintextDirectory)

    @async_unit
    async def test_creates_filesystem(self) -> None:
        await self.service.create_and_mount(name=fs_name, fstype=fs_fstype, password=fs_password,
                                            ciphertextDirectory=fs_ciphertextDirectory,
                                            plaintextDirectory=fs_plaintextDirectory)
        self.mockPlugin.create_and_mount.assert_called_once_with(ciphertextDir=fs_ciphertextDirectory,
                                                                 plaintextDir=fs_plaintextDirectory,
                                                                 password=fs_password)
