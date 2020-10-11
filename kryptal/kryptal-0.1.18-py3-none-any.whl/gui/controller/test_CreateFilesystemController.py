from PyQt5.QtWidgets import QDialog  # type: ignore
from typing import Callable, Awaitable, List
from unittest.mock import Mock
import unittest
import os
import tempfile
from kryptal.gui import Application
from kryptal.gui.controller.CreateFilesystemController import CreateFilesystemController
from kryptal.gui.view.dialogs.CreateFilesystemDialog import FsTypeEntry
from kryptal.pluginmanager.IFilesystem import FilesystemException
from kryptal.services.FilesystemCreatorService import FilesystemCreatorService
from kryptal.testutils.ApplicationHelpers import with_app_async
from unittest.mock import patch, Mock


FS_TYPE = FsTypeEntry(
    fs_type="CryFS",
    comment="recommended",
)


class CreateFilesystemDialogMock:
    def setAcceptHandler(self, acceptHandler: Callable[..., Awaitable[bool]]) -> None:
        self._acceptHandler = acceptHandler

    def whenShownAcceptWithValues(self, name: str, ciphertextDir: str, plaintextDir: str, password1: str,
                                  password2: str, fsType: FsTypeEntry) -> None:
        self._accept = True
        self._name = name
        self._ciphertextDir = ciphertextDir
        self._plaintextDir = plaintextDir
        self._password1 = password1
        self._password2 = password2
        self._fsType = fsType

    def clearPasswordFields(self) -> None:
        pass

    def whenShownDecline(self) -> None:
        self._accept = False

    def setSupportedFilesystemTypes(self, fs_types: List[FsTypeEntry]) -> None:
        pass

    async def asyncExec(self) -> int:
        if self._accept:
            await self._acceptHandler(name=self._name, ciphertextDir=self._ciphertextDir, plaintextDir=self._plaintextDir,
                                      password1=self._password1, password2=self._password2, fsType=self._fsType)
            result: int = QDialog.Accepted
        else:
            result = QDialog.Rejected
        return result


tempdir1 = tempfile.TemporaryDirectory()
tempdir2 = tempfile.TemporaryDirectory()


class test_CreateFilesystemController(unittest.TestCase):
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateFilesystemDialog', CreateFilesystemDialogMock)
    def setUp(self) -> None:
        self.serviceMock = Mock(
            spec=FilesystemCreatorService(None, None))  # type: ignore
        self.serviceMock.list_supported_filesystem_types.return_value = [
            "CryFS", "EncFS"]
        self.obj = CreateFilesystemController(self.serviceMock)

    @with_app_async
    async def test_create(self) -> None:
        self.obj._dlg.whenShownAcceptWithValues(
            "My name", tempdir1.name, tempdir2.name, "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="CryFS", ciphertextDirectory=tempdir1.name,
                                                                  plaintextDirectory=tempdir2.name,
                                                                  password="mypw".encode(
                                                                      encoding="UTF-8"))

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.QMessageBox.warning')
    async def test_passwords_dont_match_doesnt_create(self, warningBoxMock: Mock) -> None:
        self.obj._dlg.whenShownAcceptWithValues(
            "My name", tempdir1.name, tempdir2.name, "mypw1", "mypw2", FS_TYPE)
        await self.obj.create()
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.QMessageBox.warning')
    async def test_passwords_dont_match_shows_warning(self, warningBoxMock: Mock) -> None:
        self.obj._dlg.whenShownAcceptWithValues(
            "My name", tempdir1.name, tempdir2.name, "mypw1", "mypw2", FS_TYPE)
        await self.obj.create()
        self.assertEqual(1, warningBoxMock.call_count)
        self.assertTrue(
            "Passwords don't match" in warningBoxMock.call_args[0][2])

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_plaintextdir_doesnt_exist_asks_whether_should_create(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = False
        self.obj._dlg.whenShownAcceptWithValues("My name", tempdir1.name, os.path.join(tempdir2.name, "notexistingsubdir"),
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        createDirectoryQuestionMock.assert_called_once_with("plaintext directory",
                                                            os.path.join(tempdir2.name, "notexistingsubdir"))

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_plaintextdir_doesnt_exist_create(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = True
        self.obj._dlg.whenShownAcceptWithValues("My name", tempdir1.name, os.path.join(tempdir2.name, "notexistingsubdir"),
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="CryFS", ciphertextDirectory=tempdir1.name,
                                                                  plaintextDirectory=os.path.join(
                                                                      tempdir2.name, "notexistingsubdir"),
                                                                  password="mypw".encode(
                                                                      encoding="UTF-8"))

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_plaintextdir_doesnt_exist_dont_create(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = False
        self.obj._dlg.whenShownAcceptWithValues("My name", tempdir1.name, os.path.join(tempdir2.name, "notexistingsubdir"),
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_ciphertextdir_doesnt_exist_asks_whether_should_create(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = False
        self.obj._dlg.whenShownAcceptWithValues("My name", os.path.join(tempdir1.name, "notexistingsubdir"), tempdir2.name,
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        createDirectoryQuestionMock.assert_called_once_with("ciphertext directory",
                                                            os.path.join(tempdir1.name, "notexistingsubdir"))

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_ciphertextdir_doesnt_exist_create(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = True
        self.obj._dlg.whenShownAcceptWithValues("My name", os.path.join(tempdir1.name, "notexistingsubdir"), tempdir2.name,
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="CryFS",
                                                                  ciphertextDirectory=os.path.join(
                                                                      tempdir1.name, "notexistingsubdir"),
                                                                  plaintextDirectory=tempdir2.name,
                                                                  password="mypw".encode(
                                                                      encoding="UTF-8"))

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_ciphertextdir_doesnt_exist_dont_create(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = False
        self.obj._dlg.whenShownAcceptWithValues("My name", os.path.join(tempdir1.name, "notexistingsubdir"), tempdir2.name,
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_bothdirs_dont_exist_asks_whether_should_create(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = True
        self.obj._dlg.whenShownAcceptWithValues("My name", os.path.join(tempdir1.name, "notexistingsubdir"), os.path.join(tempdir2.name, "notexistingsubdir"),
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.assertEqual(2, createDirectoryQuestionMock.call_count)
        createDirectoryQuestionMock.assert_any_call(
            "ciphertext directory", os.path.join(tempdir1.name, "notexistingsubdir"))
        createDirectoryQuestionMock.assert_any_call("plaintext directory",
                                                    os.path.join(tempdir2.name, "notexistingsubdir"))

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_bothdirs_dont_exist_ask_only_once_if_declined(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = False
        self.obj._dlg.whenShownAcceptWithValues("My name", os.path.join(tempdir1.name, "notexistingsubdir"), os.path.join(tempdir2.name, "notexistingsubdir"),
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.assertEqual(1, createDirectoryQuestionMock.call_count)

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_bothdirs_dont_exist_create_both(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = True
        self.obj._dlg.whenShownAcceptWithValues("My name", os.path.join(tempdir1.name, "notexistingsubdir"), os.path.join(tempdir2.name, "notexistingsubdir"),
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="CryFS",
                                                                  ciphertextDirectory=os.path.join(
                                                                      tempdir1.name, "notexistingsubdir"),
                                                                  plaintextDirectory=os.path.join(
                                                                      tempdir2.name, "notexistingsubdir"),
                                                                  password="mypw".encode(
                                                                      encoding="UTF-8"))

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_bothdirs_dont_exist_create_one(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.side_effect = [True, False]
        self.obj._dlg.whenShownAcceptWithValues("My name", os.path.join(tempdir1.name, "notexistingsubdir"),
                                                os.path.join(
                                                    tempdir2.name, "notexistingsubdir"),
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.CreateDirectoryYesNoController.askYesNoAndCreateDir')
    async def test_bothdirs_dont_exist_create_none(self, createDirectoryQuestionMock: Mock) -> None:
        createDirectoryQuestionMock.return_value = False
        self.obj._dlg.whenShownAcceptWithValues("My name", os.path.join(tempdir1.name, "notexistingsubdir"), os.path.join(tempdir2.name, "notexistingsubdir"),
                                                "mypw", "mypw", FS_TYPE)
        await self.obj.create()
        self.assertEqual(0, self.serviceMock.create_and_mount.call_count)

    @with_app_async
    @patch('kryptal.gui.controller.CreateFilesystemController.QMessageBox.critical')
    async def test_create_error(self, criticalBoxMock: Mock) -> None:
        self.obj._dlg.whenShownAcceptWithValues(
            "My name", tempdir1.name, tempdir2.name, "mypw", "mypw", FS_TYPE)
        self.serviceMock.create_and_mount.side_effect = FilesystemException(
            "My custom error message")
        await self.obj.create()
        self.assertEqual(1, criticalBoxMock.call_count)
        self.assertEqual("My custom error message",
                         criticalBoxMock.call_args[0][2])

    @with_app_async
    async def test_choose_filesystem_type(self) -> None:
        self.obj._dlg.whenShownAcceptWithValues(
            "My name", tempdir1.name, tempdir2.name, "mypw", "mypw", FsTypeEntry(fs_type="EncFS", comment=""))
        await self.obj.create()
        self.serviceMock.create_and_mount.assert_called_once_with(name="My name", fstype="EncFS", ciphertextDirectory=tempdir1.name,
                                                                  plaintextDirectory=tempdir2.name,
                                                                  password="mypw".encode(
                                                                      encoding="UTF-8"))
