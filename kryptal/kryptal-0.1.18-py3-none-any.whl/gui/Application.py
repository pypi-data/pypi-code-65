from typing import List, Awaitable, Optional
# TODO type stubs for asyncqt
from asyncqt import QEventLoop  # type: ignore
from PyQt5.QtWidgets import QApplication  # type: ignore
import sys
import asyncio
from kryptal.gui.MainWindow import MainWindow
import kryptal.gui.TaskManager as TaskManager
from typing_extensions import Final
from kryptal.gui.view.utils.AsyncSlot import async_slot
from kryptal.gui.TrayIcon import TrayIcon
from kryptal.utils import PollProcess


class Application(QApplication):
    def __init__(self, argv: List[str]):
        super().__init__(argv)
        self.eventloop: Optional[QEventLoop] = None

    # TODO Auto-call this in run()
    def setupUncaughtExceptionHandler(self) -> None:
        sys.excepthook = TaskManager._on_uncaught_exception

    def run(self) -> int:
        assert not TaskManager.is_test_mode(), "Called Application.run but TaskManager is set to test mode"
        self.initEventLoop()
        assert self.eventloop is not None

        self.trayIcon = TrayIcon()
        self.trayIcon.onExit.connect(self.onExitButtonClick)
        self.trayIcon.show()

        self.mainWindow = MainWindow()
        self.mainWindow.show()

        with self.eventloop:
            try:
                self.eventloop.run_forever()
            finally:
                # Make sure all PollProcesses are stopped. They might otherwise still be running.
                self.eventloop.run_until_complete(PollProcess.stop_all_processes())
                # Also shutdown asyncio correctly
                self.eventloop.run_until_complete(self.eventloop.shutdown_asyncgens())
                self.eventloop.close()
                self.eventloop = None

        return 0

    @async_slot
    async def onExitButtonClick(self) -> None:
        self.quit()

    def run_for_test(self, testcase: Awaitable[None]) -> int:
        assert TaskManager.is_test_mode(), "Called Application.run_for_test but TaskManager is not set to test mode"
        self.initEventLoop()
        # don't cancel the event loop when the last window closes.
        self.setQuitOnLastWindowClosed(False)

        assert self.eventloop is not None

        # TODO with self.eventloop like in run() ?
        try:
            self.eventloop.run_until_complete(testcase)
        finally:
            # Make sure all PollProcesses are stopped. They might otherwise still be running.
            self.eventloop.run_until_complete(PollProcess.stop_all_processes())

        return 0

    def initEventLoop(self) -> None:
        if (self.eventloop is None):
            self.eventloop = QEventLoop(self)
            asyncio.set_event_loop(self.eventloop)
            self.eventloop.set_debug(True)  # TODO Disable in prod?


instance: Optional[Application] = None


def create_prod_instance() -> None:
    global instance
    TaskManager.set_is_test_mode(False)
    if instance is None:
        instance = Application(sys.argv)
    assert instance is not None


def create_test_instance() -> None:
    global instance
    TaskManager.set_is_test_mode(True)
    if instance is None:
        instance = Application(
            sys.argv + ["-platform", "offscreen"])
    assert instance is not None


def get_instance() -> Application:
    global instance
    assert instance is not None
    return instance
