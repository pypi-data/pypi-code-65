from unittest.mock import patch, Mock
from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtTest import QTest  # type: ignore
from kryptal.gui import Application
from kryptal.gui.view.widgets.DirSelector import DirSelector
from os.path import expanduser
from kryptal.testutils.ApplicationHelpers import with_app
import unittest


class test_DirSelector(unittest.TestCase):
    @with_app
    def test_init_without_error(self) -> None:
        DirSelector()

    @with_app
    def test_defaults(self) -> None:
        obj = DirSelector()
        self.assertEqual("", obj.directory())

    @with_app
    def test_set_and_get(self) -> None:
        obj = DirSelector()
        obj.setDirectory("/home/myuser")
        self.assertEqual("/home/myuser", obj.directory())

    @with_app
    def test_set_value_is_shown(self) -> None:
        obj = DirSelector()
        obj.setDirectory("/tmp")
        self.assertEqual("/tmp", obj.directoryEdit.text())

    @with_app
    def test_written_value_is_taken(self) -> None:
        obj = DirSelector()
        obj.directoryEdit.setText("/mydir/bla")
        self.assertEqual("/mydir/bla", obj.directoryEdit.text())

    @with_app
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.selectedFiles')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.exec_')
    def test_browse_button_opens_dialog(self, execMock: Mock, selectedFilesMock: Mock) -> None:
        # Have to mock this, because code-under-test calls this to get the result
        selectedFilesMock.return_value = ["/home/mydir"]
        obj = DirSelector()
        QTest.mouseClick(obj.browseButton, Qt.LeftButton)
        execMock.assert_called_once_with()

    @with_app
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.selectedFiles')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.exec_')
    def test_succeed_dialog_changes_value(self, execMock: Mock, selectedFilesMock: Mock) -> None:
        selectedFilesMock.return_value = ["/home/mydir"]
        execMock.return_value = True
        obj = DirSelector()
        obj.setDirectory("/home/otherdir")
        QTest.mouseClick(obj.browseButton, Qt.LeftButton)
        self.assertEqual("/home/mydir", obj.directory())

    @with_app
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.selectedFiles')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.exec_')
    def test_cancel_dialog_doesnt_change_value(self, execMock: Mock, selectedFilesMock: Mock) -> None:
        # Have to mock this, because code-under-test calls this to get the result
        selectedFilesMock.return_value = ["/home/mydir"]
        execMock.return_value = False
        obj = DirSelector()
        obj.setDirectory("/home/otherdir")
        QTest.mouseClick(obj.browseButton, Qt.LeftButton)
        self.assertEqual("/home/otherdir", obj.directory())

    @with_app
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.selectedFiles')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.exec_')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.setDirectory')
    def test_dialog_is_initialized_with_old_value(self, setDirectoryMock: Mock, execMock: Mock, selectedFilesMock: Mock) -> None:
        # Have to mock this, because code-under-test calls this to get the result
        selectedFilesMock.return_value = ["/home/mydir"]
        obj = DirSelector()
        obj.setDirectory("/home/otherdir")
        QTest.mouseClick(obj.browseButton, Qt.LeftButton)
        setDirectoryMock.assert_called_once_with("/home/otherdir")

    @with_app
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.selectedFiles')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.exec_')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.setDirectory')
    def test_dialog_shows_homedir_if_no_old_dir(self, setDirectoryMock: Mock, execMock: Mock, selectedFilesMock: Mock) -> None:
        # Have to mock this, because code-under-test calls this to get the result
        selectedFilesMock.return_value = ["/home/mydir"]
        obj = DirSelector()
        QTest.mouseClick(obj.browseButton, Qt.LeftButton)
        setDirectoryMock.assert_called_once_with(expanduser("~"))

    @with_app
    def test_setdirectory_doesnt_emit_directoryChanged(self) -> None:
        obj = DirSelector()
        slotMock = Mock()
        obj.directoryChanged.connect(slotMock)
        obj.setDirectory("/new/directory")
        self.assertEqual(0, slotMock.call_count)

    @with_app
    def test_editing_enter_emits_directoryChanged(self) -> None:
        obj = DirSelector()
        slotMock = Mock()
        obj.directoryChanged.connect(slotMock)
        QTest.keyClicks(obj.directoryEdit, "/new/directory")
        QTest.keyClick(obj.directoryEdit, Qt.Key_Enter)
        slotMock.assert_called_with()

    @with_app
    def test_finish_editing_emits_directoryChanged(self) -> None:
        obj = DirSelector()
        slotMock = Mock()
        obj.directoryChanged.connect(slotMock)
        obj.directoryEdit.editingFinished.emit()
        slotMock.assert_called_with()

    @with_app
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.exec_')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.setDirectory')
    def test_rejecting_dialog_doesnt_emit_directoryChanged(self, setDirectoryMock: Mock, execMock: Mock) -> None:
        execMock.return_value = False
        obj = DirSelector()
        slotMock = Mock()
        obj.directoryChanged.connect(slotMock)
        QTest.mouseClick(obj.browseButton, Qt.LeftButton)
        self.assertEqual(0, slotMock.call_count)

    @with_app
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.selectedFiles')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.exec_')
    @patch('kryptal.gui.view.widgets.DirSelector.QFileDialog.setDirectory')
    def test_accepting_dialog_emits_directoryChanged(self, setDirectoryMock: Mock, execMock: Mock, selectedFilesMock: Mock) -> None:
        execMock.return_value = True
        # Have to mock this, because code-under-test calls this to get the result
        selectedFilesMock.return_value = ["/home/mydir"]
        obj = DirSelector()
        slotMock = Mock()
        obj.directoryChanged.connect(slotMock)
        QTest.mouseClick(obj.browseButton, Qt.LeftButton)
        slotMock.assert_called_with()
