import unittest
from unittest.mock import Mock

import os
import tempfile
from kryptal.model.Filesystems import Filesystems
from kryptal.model.Filesystem import Filesystem


def assert_fs_equals(test_case: unittest.TestCase, fs: Filesystem, name: str, fstype: str, ciphertextDirectory: str, plaintextDirectory: str) -> None:
    test_case.assertEqual(name, fs.name)
    test_case.assertEqual(fstype, fs.fstype)
    test_case.assertEqual(ciphertextDirectory, fs.ciphertextDirectory)
    test_case.assertEqual(plaintextDirectory, fs.plaintextDirectory)


class test_Filesystems(unittest.TestCase):
    def setUp(self) -> None:
        self._stateTempDir = tempfile.TemporaryDirectory()
        self.model = Filesystems(os.path.join(
            self._stateTempDir.name, "filesystems.yaml"))

    def tearDown(self) -> None:
        self._stateTempDir.cleanup()

    def test_add_returnval(self) -> None:
        fs = self.model.add(name="My name 1", fstype="MyFSType1",
                            ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        assert_fs_equals(self, fs, name="My name 1", fstype="MyFSType1",
                         ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")

    def test_count_empty(self) -> None:
        self.assertEqual(0, len(self.model.filesystems()))

    def test_count_one(self) -> None:
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        self.assertEqual(1, len(self.model.filesystems()))

    def test_count_two(self) -> None:
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        self.model.add(name="My name 2", fstype="MyFSType2",
                       ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/plaintext/2")
        self.assertEqual(2, len(self.model.filesystems()))

    def test_get_one(self) -> None:
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        assert_fs_equals(self, list(self.model.filesystems().values())[
            0], name="My name 1", fstype="MyFSType1", ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")

    def test_get_two(self) -> None:
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        self.model.add(name="My name 2", fstype="MyFSType2",
                       ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/plaintext/2")
        assert_fs_equals(self, list(self.model.filesystems().values())[
            0], name="My name 1", fstype="MyFSType1", ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        assert_fs_equals(self, list(self.model.filesystems().values())[
            1], name="My name 2", fstype="MyFSType2", ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/plaintext/2")

    def test_setPlaintextDir_1(self) -> None:
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        self.model.add(name="My name 2", fstype="MyFSType2",
                       ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/plaintext/2")
        self.model.setPlaintextDirectory(list(self.model.filesystems().values())[
                                         0].id, "/my/new/plaintext/dir")
        assert_fs_equals(self, list(self.model.filesystems().values())[
            0], name="My name 1", fstype="MyFSType1", ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/new/plaintext/dir")
        assert_fs_equals(self, list(self.model.filesystems().values())[
            1], name="My name 2", fstype="MyFSType2", ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/plaintext/2")

    def test_setPlaintextDir_2(self) -> None:
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        self.model.add(name="My name 2", fstype="MyFSType2",
                       ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/plaintext/2")
        self.model.setPlaintextDirectory(list(self.model.filesystems().values())[
                                         1].id, "/my/new/plaintext/dir")
        assert_fs_equals(self, list(self.model.filesystems().values())[
            0], name="My name 1", fstype="MyFSType1", ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        assert_fs_equals(self, list(self.model.filesystems().values())[
            1], name="My name 2", fstype="MyFSType2", ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/new/plaintext/dir")

    def test_setPlaintextDir_ReturnVal(self) -> None:
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        fs = self.model.setPlaintextDirectory(list(self.model.filesystems().values())[
                                              0].id, "/my/new/plaintext/dir")
        assert_fs_equals(self, fs, name="My name 1", fstype="MyFSType1",
                         ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/new/plaintext/dir")

    def test_change_handler_add(self) -> None:
        handler = Mock()
        self.model.addChangeHandler(handler)
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        handler.assert_called_once_with()

    def test_change_handler_setPlaintextDir(self) -> None:
        handler = Mock()
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        self.model.addChangeHandler(handler)
        self.assertEqual(0, handler.call_count)
        self.model.setPlaintextDirectory(list(self.model.filesystems().values())[
                                         0].id, "/my/new/plaintext/dir")
        self.assertEqual(1, handler.call_count)

    def test_multiple_change_handler(self) -> None:
        handler1 = Mock()
        handler2 = Mock()
        self.model.addChangeHandler(handler1)
        self.model.addChangeHandler(handler2)
        self.model.add(name="My name 1", fstype="MyFSType1",
                       ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        handler1.assert_called_once_with()
        handler2.assert_called_once_with()


class test_FilesystemsIO(unittest.TestCase):
    def setUp(self) -> None:
        self._stateTempDir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._stateTempDir.name, "filesystems.yaml")

    def tearDown(self) -> None:
        self._stateTempDir.cleanup()

    def test_save_and_load_empty(self) -> None:
        Filesystems(self.path)
        obj2 = Filesystems(self.path)
        self.assertEqual(0, len(obj2.filesystems()))

    def test_save_and_load_one(self) -> None:
        obj = Filesystems(self.path)
        obj.add(name="My name 1", fstype="MyFSType1",
                ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        obj2 = Filesystems(self.path)
        self.assertEqual(1, len(obj2.filesystems()))
        assert_fs_equals(self, list(obj2.filesystems().values())[
            0], name="My name 1", fstype="MyFSType1", ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")

    def test_save_and_load_two(self) -> None:
        obj = Filesystems(self.path)
        obj.add(name="My name 1", fstype="MyFSType1",
                ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        obj.add(name="My name 2", fstype="MyFSType2",
                ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/plaintext/2")
        obj2 = Filesystems(self.path)
        self.assertEqual(2, len(obj2.filesystems()))
        assert_fs_equals(self, list(obj2.filesystems().values())[
            0], name="My name 1", fstype="MyFSType1", ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        assert_fs_equals(self, list(obj2.filesystems().values())[
            1], name="My name 2", fstype="MyFSType2", ciphertextDirectory="/my/ciphertext/2", plaintextDirectory="/my/plaintext/2")

    def test_setPlaintextDirectory_immediately_saves(self) -> None:
        obj = Filesystems(self.path)
        obj.add(name="My name 1", fstype="MyFSType1",
                ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/plaintext/1")
        obj.setPlaintextDirectory(list(obj.filesystems().values())[
                                  0].id, "/my/new/plaintext/dir")
        obj2 = Filesystems(self.path)
        assert_fs_equals(self, list(obj2.filesystems().values())[
            0], name="My name 1", fstype="MyFSType1", ciphertextDirectory="/my/ciphertext/1", plaintextDirectory="/my/new/plaintext/dir")
