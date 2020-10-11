from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtTest import QTest  # type: ignore
from kryptal.gui.view.widgets.FileSystemListItem import FileSystemListItem
from kryptal.model.Filesystem import Filesystem
from kryptal.services.FilesystemMountService import FilesystemMountService
from kryptal.testutils.ApplicationHelpers import with_app, with_app_async
from unittest.mock import Mock
from kryptal.testutils.Async import waitForConditionWithTimeout, ensureConditionInTimeout
import unittest


filesystem_fixture = Filesystem(id=0, name="My name", fstype="MyFSType",
                                ciphertextDirectory="/my/ciphertext/directory", plaintextDirectory="/my/plaintext/directory")


class test_FileSystemListItem(unittest.TestCase):
    @with_app
    def test_init_without_error(self) -> None:
        FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore

    @with_app
    def test_shown_values(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        self.assertEqual(filesystem_fixture.name, obj.nameLabel.text())
        self.assertEqual(filesystem_fixture.fstype, obj.fstypeLabel.text())
        self.assertEqual(filesystem_fixture.ciphertextDirectory,
                         obj.ciphertextDirLabel.text())
        self.assertEqual(filesystem_fixture.plaintextDirectory,
                         obj.plaintextDirSelector.directory())

    @with_app
    def test_plaintextDir(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        self.assertEqual(filesystem_fixture.plaintextDirectory,
                         obj.plaintextDir())

    @with_app
    def test_plaintextDir_changed(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        obj.plaintextDirSelector.setDirectory("/my/new/plaintext/directory")
        self.assertEqual("/my/new/plaintext/directory", obj.plaintextDir())

    @with_app
    def test_edit_plaintextDir(self) -> None:
        slotMock = Mock()
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        obj.onPlaintextDirChanged.connect(slotMock)
        obj.plaintextDirSelector.directoryChanged.emit()
        slotMock.assert_called_once_with()

    @with_app
    def test_details_initially_hidden(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        obj.show()  # Show dialog (otherwise detailsFrame.isVisible() is trivially False)
        self.assertFalse(obj.detailsFrame.isVisible())

    @with_app
    def test_details_show_on_button_click(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        obj.show()
        QTest.mouseClick(obj.detailsButton, Qt.LeftButton)
        self.assertTrue(obj.detailsFrame.isVisible())

    @with_app
    def test_details_hide_on_button_click(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        obj.show()
        QTest.mouseClick(obj.detailsButton, Qt.LeftButton)
        self.assertTrue(obj.detailsFrame.isVisible())
        QTest.mouseClick(obj.detailsButton, Qt.LeftButton)
        self.assertFalse(obj.detailsFrame.isVisible())

    @with_app
    def test_details_show_and_hide_on_name_click(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        obj.show()
        QTest.mouseClick(obj.nameLabel, Qt.LeftButton)
        self.assertTrue(obj.detailsFrame.isVisible())
        QTest.mouseClick(obj.nameLabel, Qt.LeftButton)
        self.assertFalse(obj.detailsFrame.isVisible())

    @with_app
    def test_details_show_and_hide_on_icon_click(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        obj.show()
        QTest.mouseClick(obj.icon, Qt.LeftButton)
        self.assertTrue(obj.detailsFrame.isVisible())
        QTest.mouseClick(obj.icon, Qt.LeftButton)
        self.assertFalse(obj.detailsFrame.isVisible())

    @with_app
    def test_details_show_and_hide_on_widget_click(self) -> None:
        obj = FileSystemListItem(filesystem_fixture, Mock(
            FilesystemMountService(None)))  # type: ignore
        obj.show()
        QTest.mouseClick(obj, Qt.LeftButton)
        self.assertTrue(obj.detailsFrame.isVisible())
        QTest.mouseClick(obj, Qt.LeftButton)
        self.assertFalse(obj.detailsFrame.isVisible())

    @with_app_async
    async def test_shows_initial_mount_state_false(self) -> None:
        mountServiceMock = Mock(FilesystemMountService(None))  # type: ignore
        mountServiceMock.is_mounted.return_value = False
        obj = FileSystemListItem(filesystem_fixture, mountServiceMock)
        await ensureConditionInTimeout(lambda: not obj.mountButton.isChecked(), timeout=1)
        mountServiceMock.is_mounted.assert_called_once_with(
            fstype=filesystem_fixture.fstype, ciphertextDir=filesystem_fixture.ciphertextDirectory, plaintextDir=filesystem_fixture.plaintextDirectory)

    @with_app_async
    async def test_shows_initial_mount_state_true(self) -> None:
        mountServiceMock = Mock(FilesystemMountService(None))  # type: ignore
        mountServiceMock.is_mounted.return_value = True
        obj = FileSystemListItem(filesystem_fixture, mountServiceMock)
        await ensureConditionInTimeout(obj.mountButton.isChecked, timeout=1)
        mountServiceMock.is_mounted.assert_called_once_with(
            fstype=filesystem_fixture.fstype, ciphertextDir=filesystem_fixture.ciphertextDirectory, plaintextDir=filesystem_fixture.plaintextDirectory)

    @with_app_async
    async def test_shows_changed_mount_state_false(self) -> None:
        mountServiceMock = Mock(FilesystemMountService(None))  # type: ignore
        mountServiceMock.is_mounted.return_value = True
        obj = FileSystemListItem(filesystem_fixture, mountServiceMock)
        mountServiceMock.is_mounted.return_value = False
        # trigger mount change handler
        await mountServiceMock.addChangeHandler.call_args[0][0]()
        self.assertFalse(obj.mountButton.isChecked())

    @with_app_async
    async def test_shows_changed_mount_state_true(self) -> None:
        mountServiceMock = Mock(FilesystemMountService(None))  # type: ignore
        mountServiceMock.is_mounted.return_value = False
        obj = FileSystemListItem(filesystem_fixture, mountServiceMock)
        mountServiceMock.is_mounted.return_value = True
        # trigger mount changeHandler
        await mountServiceMock.addChangeHandler.call_args[0][0]()
        self.assertTrue(obj.mountButton.isChecked())
