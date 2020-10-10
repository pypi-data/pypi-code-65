from typing import Tuple, Type
import os
import tempfile
import time
from kryptal.pluginmanager.IFilesystem import IFilesystem
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from types import TracebackType
from kryptal.testutils.ApplicationHelpers import async_unit
import asyncio
import unittest


FILESYSTEMS = [(fsname, fs)
               for (fsname, fs) in KryptalPlugins().filesystems().items()]


class TestDirs:
    def __init__(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.cipherDir = os.path.join(self.tempdir.name, "cipher")
        self.plainDir = os.path.join(self.tempdir.name, "plain")
        os.makedirs(self.cipherDir)
        os.makedirs(self.plainDir)

    def __enter__(self) -> Tuple[str, str]:
        return self.cipherDir, self.plainDir

    def __exit__(self, type_: Type[BaseException], value: BaseException, traceback: TracebackType) -> None:
        self.tempdir.cleanup()


class test_IFilesystem(unittest.TestCase):
    def test_has_name(self) -> None:
        for (fsname, filesystem) in FILESYSTEMS:
            with self.subTest(fsname):
                self.assertTrue(isinstance(filesystem.name(), str))

    @async_unit
    async def test_can_create(self) -> None:
        for (fsname, filesystem) in FILESYSTEMS:
            with self.subTest(fsname):
                with TestDirs() as (cipherDir, plainDir):
                    await filesystem.create_and_mount(
                        ciphertextDir=cipherDir,
                        plaintextDir=plainDir,
                        password="1234".encode("UTF-8")
                    )
                    # This is just here to make sure the file system is finished loading
                    await asyncio.sleep(0.25)
                    await filesystem.unmount(plainDir)

    @async_unit
    async def test_can_mount(self) -> None:
        for (fsname, filesystem) in FILESYSTEMS:
            with self.subTest(fsname):
                with TestDirs() as (cipherDir, plainDir):
                    await filesystem.create_and_mount(
                        ciphertextDir=cipherDir,
                        plaintextDir=plainDir,
                        password="1234".encode("UTF-8")
                    )
                    # This is just here to make sure the file system is finished loading
                    await asyncio.sleep(0.25)
                    await filesystem.unmount(plainDir)
                    os.makedirs(plainDir, exist_ok=True)
                    await filesystem.mount(
                        ciphertextDir=cipherDir,
                        plaintextDir=plainDir,
                        password="1234".encode("UTF-8")
                    )
                    # This is just here to make sure the file system is finished loading
                    await asyncio.sleep(0.25)
                    await filesystem.unmount(plainDir)

    # TODO Add more test cases (i.e. access mounted directory)
