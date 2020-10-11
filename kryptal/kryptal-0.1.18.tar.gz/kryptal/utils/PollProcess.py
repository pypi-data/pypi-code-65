from asyncio import create_subprocess_exec, subprocess
from asyncio.subprocess import Process
from typing import Optional, Awaitable, Callable, Dict, List
from kryptal.utils.AsyncObservable import AsyncObservable, ListenerHandle
import kryptal.gui.TaskManager as TaskManager
from typing_extensions import Final, final
import threading
import atexit
import asyncio


""" Runs an external polling process. The external process is expected to exit to notify us about a poll event.

Usage example:
def callback():
  print("Poll event happened")
pollProcess = PollProcess(["/my/poll/process/executable", "argument"])
pollProcess.addListener(callback)
pollProcess.start()
...
pollProcess.stop()

The external polling process is started and the callback called each time it exits.
You can call stop() to stop polling.
You don't have to call it though - exiting the application will also stop the external process.
"""


@final
class PollProcess:
    def __init__(self, *command: str):
        self._impl = PollProcessImpl(*command)
        self._threadident = threading.get_ident()

    def addListener(self, listener: Callable[[], Awaitable[None]]) -> ListenerHandle:
        assert threading.get_ident() == self._threadident, \
            "PollProcess is not threadsafe. Please use it on one thread only and use async/await."
        return self._impl.addListener(listener)

    def removeListener(self, handle: ListenerHandle) -> None:
        assert threading.get_ident() == self._threadident, \
            "PollProcess is not threadsafe. Please use it on one thread only and use async/await."
        return self._impl.removeListener(handle)

    def start(self) -> None:
        assert threading.get_ident() == self._threadident, \
            "PollProcess is not threadsafe. Please use it on one thread only and use async/await."
        self._impl.start()

    def stop(self) -> None:
        assert threading.get_ident() == self._threadident, \
            "PollProcess is not threadsafe. Please use it on one thread only and use async/await."
        self._impl.stop()

    def __del__(self) -> None:
        self.stop()
 

# Usually, PollProcess.__del__ should take care of stopping running PollProcesses,
# but python destructors aren't 100% reliable, so let's have an additional safety
# net to stop any remaining PollProcess instances at program exit.
_running_poll_processes: List['PollProcessImpl'] = []

async def stop_all_processes() -> None:
    # first make a copy because calling stop() removes them from the list
    processes = _running_poll_processes.copy()
    for process in processes:
        process.stop()
    assert len(_running_poll_processes) == 0


@final
class PollProcessImpl:
    def __init__(self, *command: str):
        self._command: Final = command
        self._process: Optional[Process] = None
        self._running = False
        self._should_be_running = False
        self._listeners = AsyncObservable()

    def addListener(self, listener: Callable[[], Awaitable[None]]) -> ListenerHandle:
        return self._listeners.add(listener)

    def removeListener(self, handle: ListenerHandle) -> None:
        return self._listeners.remove(handle)

    def start(self) -> None:
        self._should_be_running = True
        _running_poll_processes.append(self)
        TaskManager.create_task(self._mainLoop())

    async def _pollRound(self) -> None:
        assert self._process is None
        # TODO Make sure, poll process is terminated when kryptal is terminated (e.g. SIGINT or just normal exit), see https://gitlab.com/messmer/aeonian/commit/077b063955dc8fb8a939a0a866ee5db0b8ec1632
        self._process = await create_subprocess_exec(*self._command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await self._process.wait()
        self._process = None

    async def _mainLoop(self) -> None:
        self._running = True
        while self._should_be_running:
            await self._pollRound()
            await self._listeners.call()
        self._running = False

    def stop(self) -> None:
        if self._should_be_running:
            self._should_be_running = False
            # If the process is running, interrupt it so that _mainLoop has a chance to interrupt
            if (self._process is not None):
                try:
                    self._process.kill()
                except ProcessLookupError:
                    # This can happen if the process just got killed
                    pass
                self._process = None
            _running_poll_processes.remove(self)
    
