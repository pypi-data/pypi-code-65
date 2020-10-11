from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtTest import QTest  # type: ignore
from kryptal.gui.MainWindow import MainWindow
from kryptal.testutils.ApplicationHelpers import with_app, with_app_async
from kryptal.testutils.Async import waitForConditionWithTimeout
from unittest.mock import patch, Mock
from typing import cast
import unittest


class test_MainWindow(unittest.TestCase):
    @with_app
    def test_init_without_error(self) -> None:
        MainWindow()

    @with_app_async
    @patch('kryptal.gui.view.dialogs.CreateFilesystemDialog.CreateFilesystemDialog.asyncExec')
    async def test_show_create_filesystem_dialog(self, execDialogMock: Mock) -> None:
        window = MainWindow()
        QTest.mouseClick(window.createFilesystemButton, Qt.LeftButton)
        await waitForConditionWithTimeout(lambda: execDialogMock.call_count > 0, timeout=1)
        execDialogMock.assert_called_once_with()

    @with_app_async
    @patch('kryptal.gui.view.dialogs.AboutDialog.AboutDialog.asyncExec')
    async def test_shows_about_dialog(self, execDialogMock: Mock) -> None:
        window = MainWindow()
        QTest.mouseClick(window.aboutButton, Qt.LeftButton)
        await waitForConditionWithTimeout(lambda: execDialogMock.call_count > 0, timeout=1)
        execDialogMock.assert_called_once_with()
