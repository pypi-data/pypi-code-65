from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtTest import QTest  # type: ignore
from PyQt5.QtWidgets import QDialogButtonBox  # type: ignore
from kryptal.gui import Application
from kryptal.gui.view.dialogs.CreateFilesystemDialog import CreateFilesystemDialog, FsTypeEntry
from kryptal.testutils.ApplicationHelpers import with_app, with_app_async
from kryptal.testutils.Async import waitForConditionWithTimeout, ensureConditionInTimeout
import asyncio
import unittest
from unittest.mock import AsyncMock
from typing import Awaitable


SUPPORTED_FILESYSTEMS = [
    FsTypeEntry(
        fs_type="CryFS",
        comment="recommended",
    ),
    FsTypeEntry(
        fs_type="EncFS",
        comment="",
    )
]


class test_CreateFilesystemDialog(unittest.TestCase):
    @with_app
    def test_init_without_error(self) -> None:
        dlg = CreateFilesystemDialog()
        dlg.setSupportedFilesystemTypes(SUPPORTED_FILESYSTEMS)

    @with_app
    def test_passwords_match_indicator(self) -> None:
        dlg = CreateFilesystemDialog()
        # Dialog has to be visible, otherwise isVisible() of passwordsMatchIndicator will always be false.
        dlg.show()
        self.assertFalse(dlg.passwordsMatchIndicator.isVisible())
        dlg.password1Edit.setText("pw1")
        self.assertTrue(dlg.passwordsMatchIndicator.isVisible())
        dlg.password2Edit.setText("pw2")
        self.assertTrue(dlg.passwordsMatchIndicator.isVisible())
        dlg.password1Edit.setText("pw2")
        self.assertFalse(dlg.passwordsMatchIndicator.isVisible())
        dlg.password2Edit.setText("pw1")
        self.assertTrue(dlg.passwordsMatchIndicator.isVisible())
        dlg.password1Edit.setText("pw2")
        self.assertTrue(dlg.passwordsMatchIndicator.isVisible())
        dlg.password1Edit.setText("pw1")
        self.assertFalse(dlg.passwordsMatchIndicator.isVisible())

    @with_app
    def test_clear_password_fields(self) -> None:
        dlg = CreateFilesystemDialog()
        dlg.password1Edit.setText("pw1")
        dlg.password2Edit.setText("pw2")
        dlg.clearPasswordFields()
        self.assertEqual("", dlg.password1Edit.text())
        self.assertEqual("", dlg.password2Edit.text())

    @with_app_async
    async def test_default_acceptor_just_accepts(self) -> None:
        dlg = CreateFilesystemDialog()
        dlg.setSupportedFilesystemTypes(SUPPORTED_FILESYSTEMS)
        asyncio.ensure_future(dlg.asyncExec())
        await waitForConditionWithTimeout(dlg.isVisible, timeout=1)
        QTest.keyClick(dlg, Qt.Key_Enter)
        await waitForConditionWithTimeout(lambda: not dlg.isVisible(), timeout=1)


class test_CreateFilesystemDialog_WithCustomAcceptHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.acceptHandlerMock = AsyncMock()
        self.acceptHandlerMock.return_value = True
        self.dlg = CreateFilesystemDialog()
        self.dlg.setSupportedFilesystemTypes(SUPPORTED_FILESYSTEMS)
        self.dlg.setAcceptHandler(self.acceptHandlerMock)

    async def show_dialog(self) -> Awaitable[int]:
        handle = asyncio.ensure_future(self.dlg.asyncExec())
        await waitForConditionWithTimeout(self.dlg.isVisible, timeout=1)
        return handle

    def accept_dialog(self) -> None:
        QTest.mouseClick(self.dlg.dialogButtons.button(
            QDialogButtonBox.Ok), Qt.LeftButton)

    def decline_dialog(self) -> None:
        QTest.mouseClick(self.dlg.dialogButtons.button(
            QDialogButtonBox.Cancel), Qt.LeftButton)

    @with_app_async
    async def test_accept_dialog(self) -> None:
        handle = await self.show_dialog()
        self.accept_dialog()
        await waitForConditionWithTimeout(lambda: not self.dlg.isVisible(), timeout=1)
        self.assertEqual(1, self.acceptHandlerMock.call_count)
        await handle

    @with_app_async
    async def test_decline_dialog(self) -> None:
        handle = await self.show_dialog()
        self.decline_dialog()
        await waitForConditionWithTimeout(lambda: not self.dlg.isVisible(), timeout=1)
        self.assertEqual(0, self.acceptHandlerMock.call_count)
        await handle

    @with_app_async
    async def test_custom_true_acceptor(self) -> None:
        self.acceptHandlerMock.return_value = True
        handle = await self.show_dialog()
        self.accept_dialog()
        await waitForConditionWithTimeout(lambda: not self.dlg.isVisible(), timeout=1)
        await handle

    @with_app_async
    async def test_custom_false_acceptor(self) -> None:
        self.acceptHandlerMock.return_value = False
        handle = await self.show_dialog()
        self.accept_dialog()
        await ensureConditionInTimeout(self.dlg.isVisible, timeout=1)
        # test finished, now cleanly shutdown the dialog
        self.acceptHandlerMock.return_value = True
        self.accept_dialog()
        await handle

    @with_app_async
    async def test_custom_acceptor_parameters(self) -> None:
        handle = await self.show_dialog()
        self.dlg.nameEdit.setText("MyName")
        self.dlg.ciphertextDirSelector.setDirectory("/my/ciphertext/dir")
        self.dlg.plaintextDirSelector.setDirectory("/my/plaintext/dir")
        self.dlg.password1Edit.setText("MyPassword1")
        self.dlg.password2Edit.setText("MyPassword2")
        self.dlg.filesystemTypeComboBox.setCurrentIndex(1)
        self.accept_dialog()
        await waitForConditionWithTimeout(lambda: not self.dlg.isVisible(), timeout=1)
        self.acceptHandlerMock.assert_called_once_with(
            name="MyName", ciphertextDir="/my/ciphertext/dir", plaintextDir="/my/plaintext/dir",
            password1="MyPassword1", password2="MyPassword2", fsType=FsTypeEntry(
                fs_type="EncFS",
                comment="",
            ))
        await handle

    @with_app_async
    async def test_enter_accepts(self) -> None:
        handle = await self.show_dialog()
        QTest.keyClick(self.dlg, Qt.Key_Enter)
        await waitForConditionWithTimeout(lambda: not self.dlg.isVisible(), timeout=1)
        self.assertEqual(1, self.acceptHandlerMock.call_count)
        await handle

    @with_app_async
    async def test_esc_declines(self) -> None:
        handle = await self.show_dialog()
        QTest.keyClick(self.dlg, Qt.Key_Escape)
        await waitForConditionWithTimeout(lambda: not self.dlg.isVisible(), timeout=1)
        self.assertEqual(0, self.acceptHandlerMock.call_count)
        await handle

    @with_app_async
    async def test_close_declines(self) -> None:
        handle = await self.show_dialog()
        self.dlg.close()
        await waitForConditionWithTimeout(lambda: not self.dlg.isVisible(), timeout=1)
        self.assertEqual(0, self.acceptHandlerMock.call_count)
        await handle
