from typing import Sequence

import pkg_resources
from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtTest import QTest  # type: ignore
from PyQt5.QtWidgets import QDialogButtonBox  # type:ignore
from kryptal.gui.view.dialogs.AboutDialog import AboutDialog
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from kryptal.testutils.ApplicationHelpers import with_app, with_app_async
import asyncio
from kryptal.testutils.Async import waitForConditionWithTimeout
import unittest


def assert_items_equal(testcase: unittest.TestCase, expected: Sequence[str], actual: Sequence[str]) -> None:
    testcase.assertEqual(sorted(expected), sorted(actual))


class test_AboutDialog(unittest.TestCase):
    @with_app
    def test_init_without_error(self) -> None:
        plugins = KryptalPlugins()
        AboutDialog(plugins)

    @with_app_async
    async def test_close_button(self) -> None:
        dlg = AboutDialog(KryptalPlugins())
        asyncio.ensure_future(dlg.asyncExec())
        await waitForConditionWithTimeout(dlg.isVisible, timeout=1)
        QTest.mouseClick(dlg.buttonBox.button(
            QDialogButtonBox.Close), Qt.LeftButton)
        await waitForConditionWithTimeout(lambda: not dlg.isVisible(), timeout=1)

    @with_app_async
    async def test_asyncExec(self) -> None:
        dlg = AboutDialog(KryptalPlugins())
        fut = asyncio.ensure_future(dlg.asyncExec())
        await waitForConditionWithTimeout(dlg.isVisible, timeout=1)
        self.assertFalse(fut.done())
        QTest.mouseClick(dlg.buttonBox.button(
            QDialogButtonBox.Close), Qt.LeftButton)
        await waitForConditionWithTimeout(lambda: not dlg.isVisible(), timeout=1)
        self.assertTrue(fut.done())

    @with_app
    def test_shows_filesystem_plugins(self) -> None:
        plugins = KryptalPlugins()
        dlg = AboutDialog(plugins)
        expected = [fs.name() for fs in plugins.filesystems().values()]
        actual = [dlg.filesystemsList.item(index).text(
        ) for index in range(dlg.filesystemsList.count())]
        assert_items_equal(self, expected, actual)

    @with_app
    def test_shows_storage_plugins(self) -> None:
        plugins = KryptalPlugins()
        dlg = AboutDialog(plugins)
        expected = [sp.name() for sp in plugins.storage_providers().values()]
        actual = [dlg.storagesList.item(index).text()
                  for index in range(dlg.storagesList.count())]
        assert_items_equal(self, expected, actual)

    @with_app
    def test_shows_version(self) -> None:
        dlg = AboutDialog(KryptalPlugins())
        self.assertEqual(pkg_resources.require("Kryptal")[
            0].version, dlg.versionLabel.text())
