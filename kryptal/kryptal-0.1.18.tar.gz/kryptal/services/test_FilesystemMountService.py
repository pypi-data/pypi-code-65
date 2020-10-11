from unittest.mock import create_autospec, Mock
import os
import tempfile
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from kryptal.services.FilesystemMountService import FilesystemMountService
from kryptal.testutils.ApplicationHelpers import async_unit
from .DummyFilesystem import DummyFilesystem
import unittest


fs_fstype = "MyFSType"
fs_ciphertextDirectory = "my/ciphertext/dir"
fs_plaintextDirectory = "my/plaintext/dir"
fs_password = "mypassword".encode(encoding="UTF-8")


class test_FilesystemMountService(unittest.TestCase):
    def setUp(self) -> None:
        self.plugins = Mock(KryptalPlugins())
        self.fsplugin = Mock(DummyFilesystem())
        self.plugins.filesystems.return_value = {
            fs_fstype: self.fsplugin, "other": Mock(DummyFilesystem)}
        self.obj = FilesystemMountService(self.plugins)
        self.tempdir = tempfile.TemporaryDirectory()
        self.ciphertextDir = os.path.join(
            self.tempdir.name, fs_ciphertextDirectory)
        self.plaintextDir = os.path.join(
            self.tempdir.name, fs_plaintextDirectory)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    async def mount(self) -> None:
        await self.obj.mount(fstype=fs_fstype, ciphertextDir=self.ciphertextDir, plaintextDir=self.plaintextDir, password=fs_password)

    async def unmount(self) -> None:
        await self.obj.unmount(fstype=fs_fstype, plaintextDir=self.plaintextDir)

    async def is_mounted(self) -> bool:
        return await self.obj.is_mounted(fstype=fs_fstype, plaintextDir=self.plaintextDir, ciphertextDir=self.ciphertextDir)

    @async_unit
    async def test_mount(self) -> None:
        await self.mount()
        self.fsplugin.mount.assert_called_once_with(
            ciphertextDir=self.ciphertextDir, plaintextDir=self.plaintextDir, password=fs_password)

    @async_unit
    async def test_mount_creates_plaintextDir(self) -> None:
        self.assertFalse(os.path.isdir(self.plaintextDir))
        await self.mount()
        self.assertTrue(os.path.isdir(self.plaintextDir))

    @async_unit
    async def test_unmount(self) -> None:
        await self.unmount()
        self.fsplugin.unmount.assert_called_once_with(
            plaintextDir=self.plaintextDir)

    @async_unit
    async def test_is_mounted_params(self) -> None:
        await self.is_mounted()
        self.fsplugin.is_mounted.assert_called_once_with(
            plaintextDir=self.plaintextDir, ciphertextDir=self.ciphertextDir)

    @async_unit
    async def test_is_mounted_true(self) -> None:
        self.fsplugin.is_mounted.return_value = True
        self.assertEqual(True, await self.is_mounted())

    @async_unit
    async def test_is_mounted_false(self) -> None:
        self.fsplugin.is_mounted.return_value = False
        self.assertEqual(False, await self.is_mounted())
