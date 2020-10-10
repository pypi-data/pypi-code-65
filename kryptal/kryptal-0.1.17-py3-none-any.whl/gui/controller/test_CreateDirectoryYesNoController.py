import stat
from unittest.mock import patch, Mock
import os
import tempfile
from PyQt5.QtCore import QObject  # type: ignore
from PyQt5.QtWidgets import QMessageBox  # type: ignore
from kryptal.gui import Application
from kryptal.gui.controller.CreateDirectoryYesNoController import CreateDirectoryYesNoController
from kryptal.testutils.ApplicationHelpers import with_app
import unittest


class test_CreateDirectoryYesNoController(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.dir_to_create = os.path.join(self.tempdir.name, "mydirname")
    
    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @with_app
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_create(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        obj = CreateDirectoryYesNoController(None)
        obj.askYesNoAndCreateDir("Mydir", self.dir_to_create)
        self.assertTrue(os.path.isdir(self.dir_to_create))

    @with_app
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_create_returnval(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        obj = CreateDirectoryYesNoController(None)
        self.assertTrue(obj.askYesNoAndCreateDir("Mydir", self.dir_to_create))

    @with_app
    @patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_create_with_subdir(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        obj = CreateDirectoryYesNoController(None)
        self.assertTrue(obj.askYesNoAndCreateDir(
                        "Mydir", os.path.join(self.dir_to_create, "subdir")))
        self.assertTrue(os.path.isdir(
            os.path.join(self.dir_to_create, "subdir")))

    @ with_app
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_dont_create(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.No
        obj = CreateDirectoryYesNoController(None)
        not obj.askYesNoAndCreateDir("Mydir", self.dir_to_create)
        self.assertFalse(os.path.isdir(self.dir_to_create))

    @ with_app
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_dont_create_returnval(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.No
        obj = CreateDirectoryYesNoController(None)
        self.assertFalse(obj.askYesNoAndCreateDir(
            "Mydir", self.dir_to_create))

    @ with_app
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_msgbox_parent(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.No
        parent = QObject()
        obj = CreateDirectoryYesNoController(parent)
        obj.askYesNoAndCreateDir("Mydir", self.dir_to_create)
        self.assertEqual(1, questionBoxMock.call_count)
        self.assertEqual(parent, questionBoxMock.call_args[0][0])

    @ with_app
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_msgbox_text(self, questionBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.No
        obj = CreateDirectoryYesNoController(None)
        obj.askYesNoAndCreateDir("Mydir", self.dir_to_create)
        self.assertEqual(1, questionBoxMock.call_count)
        self.assertTrue("Mydir" in questionBoxMock.call_args[0][2])

    @ with_app
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.warning')
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_missing_permissions_showswarning(self, questionBoxMock: Mock, warningBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        os.chmod(self.tempdir.name, 0)
        obj = CreateDirectoryYesNoController(None)
        obj.askYesNoAndCreateDir("Mydir", self.dir_to_create)
        self.assertEqual(1, warningBoxMock.call_count)
        self.assertTrue(
            "missing permissions" in warningBoxMock.call_args[0][2])
        # reset permissions (otherwise tempdir can't be cleaned up)
        os.chmod(self.tempdir.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    @ with_app
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.warning')
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_missing_permissions_returnval(self, questionBoxMock: Mock, warningBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        os.chmod(self.tempdir.name, 0)
        obj = CreateDirectoryYesNoController(None)
        self.assertFalse(obj.askYesNoAndCreateDir(
            "Mydir", self.dir_to_create))
        # reset permissions (otherwise tempdir can't be cleaned up)
        os.chmod(self.tempdir.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    @ with_app
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.warning')
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_invalid_dir_showswarning(self, questionBoxMock: Mock, warningBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        obj = CreateDirectoryYesNoController(None)
        obj.askYesNoAndCreateDir("Mydir", "")
        self.assertEqual(1, warningBoxMock.call_count)
        self.assertTrue("Couldn't create" in warningBoxMock.call_args[0][2])

    @ with_app
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.warning')
    @ patch('kryptal.gui.controller.CreateDirectoryYesNoController.QMessageBox.question')
    def test_invalid_dir_returnval(self, questionBoxMock: Mock, warningBoxMock: Mock) -> None:
        questionBoxMock.return_value = QMessageBox.Yes
        obj = CreateDirectoryYesNoController(None)
        self.assertFalse(obj.askYesNoAndCreateDir("Mydir", ""))
