import unittest
import os
import tempfile
from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtTest import QTest  # type: ignore
from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox  # type: ignore
from kryptal.gui import Application
from kryptal.gui.controller.CreateFilesystemController import CreateFilesystemController
from kryptal.gui.view.dialogs.CreateFilesystemDialog import FsTypeEntry
from kryptal.pluginmanager.IFilesystem import FilesystemException
from kryptal.services.FilesystemCreatorService import FilesystemCreatorService
from kryptal.testutils.ApplicationHelpers import with_app, with_app_async
from kryptal.testutils.Async import waitForConditionWithTimeout, ensureConditionInTimeout
from unittest.mock import Mock, patch
import asyncio
from typing import Callable, Awaitable


FS_TYPES = [
    FsTypeEntry(
        fs_type="CryFS",
        comment="recommended",
    ),
    FsTypeEntry(
        fs_type="EncFS",
        comment="",
    ),
]


class test_CreateFilesystem_Integration(unittest.TestCase):
    def setUp(self) -> None:
        self.serviceMock = Mock(
            FilesystemCreatorService(None, None))  # type: ignore
        self.serviceMock.list_supported_filesystem_types.return_value = [
            "CryFS", "EncFS"]
        self.createFilesystemController = CreateFilesystemController(
            self.serviceMock)
        self.tempdir1 = tempfile.TemporaryDirectory()
        self.tempdir2 = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir1.cleanup()
        self.tempdir2.cleanup()

    async def showDialog(self) -> Awaitable[None]:
        # Schedule dialog display
        handle = asyncio.ensure_future(self.createFilesystemController.create())
        await self.expectDialogVisible(timeout=1)
        return handle

    async def expectDialogVisible(self, timeout: float) -> None:
        await waitForConditionWithTimeout(self.createFilesystemController._dlg.isVisible, timeout=timeout)

    async def expectDialogNotVisible(self, timeout: float) -> None:
        await waitForConditionWithTimeout(lambda: not self.createFilesystemController._dlg.isVisible(), timeout=timeout)

    async def expectDialogStaysVisible(self, timeout: float) -> None:
        await ensureConditionInTimeout(self.createFilesystemController._dlg.isVisible, timeout=timeout)

    def setDialogValues(self, name: str, ciphertextDir: str, plaintextDir: str, password1: str, password2: str, fsType: FsTypeEntry) -> None:
        self.createFilesystemController._dlg.nameEdit.setText(name)
        self.createFilesystemController._dlg.ciphertextDirSelector.directoryEdit.setText(
            ciphertextDir)
        self.createFilesystemController._dlg.plaintextDirSelector.directoryEdit.setText(
            plaintextDir)
        self.createFilesystemController._dlg.password1Edit.setText(password1)
        self.createFilesystemController._dlg.password2Edit.setText(password2)
        self.createFilesystemController._dlg.filesystemTypeComboBox.setCurrentIndex(
            FS_TYPES.index(fsType)
        )

    def acceptDialog(self) -> None:
        QTest.mouseClick(self.createFilesystemController._dlg.dialogButtons.button(
            QDialogButtonBox.Ok), Qt.LeftButton)

    def declineDialog(self) -> None:
        QTest.mouseClick(self.createFilesystemController._dlg.dialogButtons.button(QDialogButtonBox.Cancel),
                         Qt.LeftButton)

    async def showAndAcceptDialogWith(self, name: str, ciphertextDir: str, plaintextDir: str, password1: str,
                                      password2: str, fsType: FsTypeEntry) -> Awaitable[None]:
        handle = await self.showDialog()
        self.setDialogValues(name=name, ciphertextDir=ciphertextDir, plaintextDir=plaintextDir, password1=password1,
                             password2=password2, fsType=fsType)
        self.acceptDialog()
        return handle

    @with_app_async
    async def test_accept_creates(self) -> None:
        handle = await self.showDialog()
        self.setDialogValues(name="My name", ciphertextDir=self.tempdir1.name, plaintextDir=self.tempdir2.name,
                             password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        self.acceptDialog()
        await self.expectDialogNotVisible(timeout=1)
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="CryFS",
                                                                  ciphertextDirectory=self.tempdir1.name,
                                                                  plaintextDirectory=self.tempdir2.name,
                                                                  password="mypw".encode(
                                                                      encoding="UTF-8"))
        await handle

    @with_app_async
    async def test_decline_doesnt_create(self) -> None:
        handle = await self.showDialog()
        self.setDialogValues(name="My name", ciphertextDir=self.tempdir1.name, plaintextDir=self.tempdir2.name,
                             password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        self.declineDialog()
        await self.expectDialogNotVisible(timeout=1)
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.QMessageBox.warning')
    async def test_passwords_mismatch(self, warningBoxMock: Mock) -> None:
        handle = await self.showAndAcceptDialogWith(name="My name", ciphertextDir=self.tempdir1.name, plaintextDir=self.tempdir2.name,
                                           password1="mypw1", password2="mypw2", fsType=FS_TYPES[0])
        await self.expectDialogStaysVisible(timeout=1)
        await waitForConditionWithTimeout(lambda: warningBoxMock.call_count == 1, timeout=1)
        self.assertTrue(
            "Passwords don't match" in warningBoxMock.call_args[0][2])
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)
        await self.expectDialogStaysVisible(timeout=1)
        # test case finished, clean up
        self.createFilesystemController._dlg.reject()
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    async def test_plaintextdir_doesnt_exist_create(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        handle = await self.showAndAcceptDialogWith(name="My name", ciphertextDir=self.tempdir1.name,
                                                    plaintextDir=os.path.join(
                                                        self.tempdir2.name, "notexistingsubdir"),
                                                    password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        await waitForConditionWithTimeout(lambda: questionBoxMock.call_count == 1, timeout=1)
        # Assert "Do you want to create the directory?" was asked
        self.assertTrue(
            "plaintext directory" in questionBoxMock.call_args[0][2])
        await self.expectDialogNotVisible(timeout=1)  # Assert dialog closed
        # Assert dir was created
        self.assertTrue(os.path.isdir(os.path.join(
                                      self.tempdir2.name, "notexistingsubdir")))
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="CryFS",
                                                                  # Assert filesystem was created
                                                                  ciphertextDirectory=self.tempdir1.name,
                                                                  plaintextDirectory=os.path.join(self.tempdir2.name,
                                                                                                  "notexistingsubdir"),
                                                                  password="mypw".encode(encoding="UTF-8"))
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    async def test_plaintextdir_doesnt_exist_dont_create(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.No
        handle = await self.showAndAcceptDialogWith(name="My name", ciphertextDir=self.tempdir1.name,
                                                    plaintextDir=os.path.join(
                                                        self.tempdir2.name, "notexistingsubdir"),
                                                    password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        # Assert "Do you want to create the directory?" was asked
        await waitForConditionWithTimeout(lambda: questionBoxMock.call_count == 1, timeout=1)
        self.assertTrue(
            "plaintext directory" in questionBoxMock.call_args[0][2])
        # Assert dialog still open
        await self.expectDialogStaysVisible(timeout=1)
        # Assert dir was not created
        self.assertFalse(os.path.isdir(os.path.join(
            self.tempdir2.name, "notexistingsubdir")))
        # Assert filesystem was not created
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)
        # test case finished, clean up
        self.createFilesystemController._dlg.reject()
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    async def test_ciphertextdir_doesnt_exist_create(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        handle = await self.showAndAcceptDialogWith(name="My name",
                                                    ciphertextDir=os.path.join(
                                                        self.tempdir1.name, "notexistingsubdir"),
                                                    plaintextDir=self.tempdir2.name, password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        # Assert "Do you want to create the directory?" was asked
        await waitForConditionWithTimeout(lambda: questionBoxMock.call_count == 1, timeout=1)
        self.assertTrue(
            "ciphertext directory" in questionBoxMock.call_args[0][2])
        await self.expectDialogNotVisible(timeout=1)  # Assert dialog closed
        # Assert dir was created
        self.assertTrue(os.path.isdir(os.path.join(
                                      self.tempdir1.name, "notexistingsubdir")))
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="CryFS",
                                                                  # Assert filesystem was created
                                                                  ciphertextDirectory=os.path.join(self.tempdir1.name,
                                                                                                   "notexistingsubdir"),
                                                                  plaintextDirectory=self.tempdir2.name,
                                                                  password="mypw".encode(encoding="UTF-8"))
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    async def test_ciphertextdir_doesnt_exist_dont_create(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.No
        handle = await self.showAndAcceptDialogWith(name="My name",
                                                    ciphertextDir=os.path.join(
                                                        self.tempdir1.name, "notexistingsubdir"),
                                                    plaintextDir=self.tempdir2.name, password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        # Assert "Do you want to create the directory?" was asked
        await waitForConditionWithTimeout(lambda: questionBoxMock.call_count == 1, timeout=1)
        self.assertTrue(
            "ciphertext directory" in questionBoxMock.call_args[0][2])
        # Assert dialog still open
        await self.expectDialogStaysVisible(timeout=1)
        # Assert dir was not created
        self.assertFalse(os.path.isdir(os.path.join(
            self.tempdir1.name, "notexistingsubdir")))
        # Assert filesystem was not created
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)
        # test case finished, clean up
        self.createFilesystemController._dlg.reject()
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    async def test_bothdirs_dont_exist_create_both(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        handle = await self.showAndAcceptDialogWith(name="My name",
                                                    ciphertextDir=os.path.join(
                                                        self.tempdir1.name, "notexistingsubdir"),
                                                    plaintextDir=os.path.join(
                                                        self.tempdir2.name, "notexistingsubdir"),
                                                    password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        # Assert "Do you want to create the directory?" was asked twice
        await waitForConditionWithTimeout(lambda: questionBoxMock.call_count == 2, timeout=1)
        await self.expectDialogNotVisible(timeout=1)  # Assert dialog closed
        # Assert ciphertext dir was created
        self.assertTrue(os.path.isdir(os.path.join(
                                      self.tempdir1.name, "notexistingsubdir")))
        # Assert plaintext dir was created
        self.assertTrue(os.path.isdir(os.path.join(
                                      self.tempdir2.name, "notexistingsubdir")))
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="CryFS",  # Assert filesystem was created
                                                                  ciphertextDirectory=os.path.join(
                                                                      self.tempdir1.name, "notexistingsubdir"),
                                                                  plaintextDirectory=os.path.join(
                                                                      self.tempdir2.name, "notexistingsubdir"),
                                                                  password="mypw".encode(encoding="UTF-8"))
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    async def test_bothdirs_dont_exist_create_one(self, questionBoxMock: Mock) -> None:
        questionBoxMock.side_effect = [QMessageBox.Yes, QMessageBox.No]
        handle = await self.showAndAcceptDialogWith(name="My name",
                                                    ciphertextDir=os.path.join(
                                                        self.tempdir1.name, "notexistingsubdir"),
                                                    plaintextDir=os.path.join(
                                                        self.tempdir2.name, "notexistingsubdir"),
                                                    password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        # Assert "Do you want to create the directory?" was asked twice
        await waitForConditionWithTimeout(lambda: questionBoxMock.call_count == 2, timeout=1)
        # Assert dialog still open
        await self.expectDialogStaysVisible(timeout=1)
        # Assert filesystem was not created
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)
        # test case finished, clean up
        self.createFilesystemController._dlg.reject()
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    async def test_bothdirs_dont_exist_create_none(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.No
        handle = await self.showAndAcceptDialogWith(name="My name",
                                                    ciphertextDir=os.path.join(
                                                        self.tempdir1.name, "notexistingsubdir"),
                                                    plaintextDir=os.path.join(
                                                        self.tempdir2.name, "notexistingsubdir"),
                                                    password1="mypw", password2="mypw", fsType=FS_TYPES[0])
        # Assert "Do you want to create the directory?" was asked once
        await waitForConditionWithTimeout(lambda: questionBoxMock.call_count == 1, timeout=1)
        # Assert "Do you want to create the directory?" was not asked a second time
        await ensureConditionInTimeout(lambda: questionBoxMock.call_count == 1, timeout=1)
        # Assert dialog still open
        await self.expectDialogStaysVisible(timeout=1)
        # Assert ciphertext dir was not created
        self.assertFalse(os.path.isdir(os.path.join(
            self.tempdir1.name, "notexistingsubdir")))
        # Assert plaintextdir was not created
        self.assertFalse(os.path.isdir(os.path.join(
            self.tempdir2.name, "notexistingsubdir")))
        # Assert filesystem was not created
        self.assertTrue(self.serviceMock.create_and_mount.call_count == 0)
        # test case finished, clean up
        self.createFilesystemController._dlg.reject()
        await handle

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.QMessageBox.critical')
    async def test_create_error(self, criticalBoxMock: Mock) -> None:
        self.serviceMock.create_and_mount.side_effect = FilesystemException(
            "My custom error message")
        handle = await self.showAndAcceptDialogWith("My name", self.tempdir1.name, self.tempdir2.name, "mypw", "mypw", fsType=FS_TYPES[0])
        # Assert error message was shown
        await waitForConditionWithTimeout(lambda: criticalBoxMock.call_count == 1, timeout=1)
        self.assertEqual("My custom error message",
                         criticalBoxMock.call_args[0][2])
        # Assert dialog still open
        await self.expectDialogStaysVisible(timeout=1)
        # test case finished, clean up
        self.createFilesystemController._dlg.reject()
        await handle
