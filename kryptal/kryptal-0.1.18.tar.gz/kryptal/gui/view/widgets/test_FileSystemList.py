import unittest
from unittest.mock import create_autospec

import os
import tempfile
from kryptal.gui.view.widgets.FileSystemList import FileSystemList
from kryptal.gui.view.widgets.FileSystemListItem import FileSystemListItem
from kryptal.model.Filesystems import Filesystems
from kryptal.services.FilesystemMountService import FilesystemMountService
from kryptal.testutils.ApplicationHelpers import with_app
from kryptal.gui.controller.RemoveFilesystemController import RemoveFilesystemController


class test_FileSystemList_1(unittest.TestCase):
    @with_app
    def test_init_without_error(self) -> None:
        FileSystemList()


class test_FileSystemList(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.model = Filesystems(os.path.join(
            self._tempdir.name, "filesystems.json"))

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def num_filesystems(self, fs: FileSystemList) -> int:
        count = 0
        for i in range(fs._layout.count()):
            if isinstance(fs._layout.itemAt(i).widget(), FileSystemListItem):
                count = count + 1
        return count

    @with_app
    def test_init_empty(self) -> None:
        obj = FileSystemList()
        self.assertEqual(0, self.num_filesystems(obj))

    @with_app
    def test_set_empty_model(self) -> None:
        obj = FileSystemList()
        obj.init(self.model, create_autospec(FilesystemMountService),
                 create_autospec(RemoveFilesystemController))
        self.assertEqual(0, self.num_filesystems(obj))

    @with_app
    def test_set_oneitem_model(self) -> None:
        self.model.add(name="My name", fstype="MyFSType", plaintextDirectory="/my/plaintext/dir",
                       ciphertextDirectory="/my/ciphertext/dir")
        obj = FileSystemList()
        obj.init(self.model, create_autospec(FilesystemMountService),
                 create_autospec(RemoveFilesystemController))
        self.assertEqual(1, self.num_filesystems(obj))

    @with_app
    def test_set_twoitem_model(self) -> None:
        self.model.add(name="My name", fstype="MyFSType", plaintextDirectory="/my/plaintext/dir",
                       ciphertextDirectory="/my/ciphertext/dir")
        self.model.add(name="My name", fstype="MyFSType", plaintextDirectory="/my/plaintext/dir",
                       ciphertextDirectory="/my/ciphertext/dir")
        obj = FileSystemList()
        obj.init(self.model, create_autospec(FilesystemMountService),
                 create_autospec(RemoveFilesystemController))
        self.assertEqual(2, self.num_filesystems(obj))

    @with_app
    def test_add_item(self) -> None:
        obj = FileSystemList()
        obj.init(self.model, create_autospec(FilesystemMountService),
                 create_autospec(RemoveFilesystemController))
        self.model.add(name="My name", fstype="MyFSType", plaintextDirectory="/my/plaintext/dir",
                       ciphertextDirectory="/my/ciphertext/dir")
        self.assertEqual(1, self.num_filesystems(obj))

    @with_app
    def test_add_two_items(self) -> None:
        obj = FileSystemList()
        obj.init(self.model, create_autospec(FilesystemMountService),
                 create_autospec(RemoveFilesystemController))
        self.model.add(name="My name", fstype="MyFSType", plaintextDirectory="/my/plaintext/dir",
                       ciphertextDirectory="/my/ciphertext/dir")
        self.model.add(name="My name", fstype="MyFSType", plaintextDirectory="/my/plaintext/dir",
                       ciphertextDirectory="/my/ciphertext/dir")
        self.assertEqual(2, self.num_filesystems(obj))

    @with_app
    def test_change_plaintextDir_in_view_updates_model(self) -> None:
        obj = FileSystemList()
        self.model.add(name="My name", fstype="MyFSType", plaintextDirectory="/my/plaintext/dir",
                       ciphertextDirectory="/my/ciphertext/dir")
        obj.init(self.model, create_autospec(FilesystemMountService),
                 create_autospec(RemoveFilesystemController))
        obj._layout.itemAt(0).widget().plaintextDirSelector.setDirectory(
            "/my/new/plaintext/dir")
        obj._layout.itemAt(0).widget(
        ).plaintextDirSelector.directoryChanged.emit()
        self.assertEqual("/my/new/plaintext/dir",
                         list(self.model.filesystems().values())[0].plaintextDirectory)

    @with_app
    def test_change_plaintextDir_in_model_updates_view(self) -> None:
        obj = FileSystemList()
        self.model.add(name="My name", fstype="MyFSType", plaintextDirectory="/my/plaintext/dir",
                       ciphertextDirectory="/my/ciphertext/dir")
        obj.init(self.model, create_autospec(FilesystemMountService),
                 create_autospec(RemoveFilesystemController))
        self.model.setPlaintextDirectory(list(self.model.filesystems().keys())[
                                         0], "/my/new/plaintext/dir")
        self.assertEqual("/my/new/plaintext/dir",
                         obj._layout.itemAt(0).widget().plaintextDirSelector.directory())
