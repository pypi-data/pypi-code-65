import asyncio, sys
import traceback as _traceback
from asyncio import Future
from typing import TYPE_CHECKING, Awaitable, TypeVar, Type
from types import TracebackType
from PyQt5.QtWidgets import QMessageBox  # type: ignore
import kryptal.gui.TaskManager


T = TypeVar('T')
if TYPE_CHECKING:
    _FutureOfNone = Future[None]
else:
    _FutureOfNone = Future


_is_test_mode: bool = False


def set_is_test_mode(is_test_mode: bool) -> None:
    global _is_test_mode
    _is_test_mode = is_test_mode

def is_test_mode() -> bool:
    global _is_test_mode
    return _is_test_mode


def create_task(future: Awaitable[None]) -> _FutureOfNone:
    if _is_test_mode:
        return asyncio.ensure_future(future)
    else:
        return asyncio.ensure_future(_exception_wrapper(future))


async def _exception_wrapper(future: Awaitable[None]) -> None:
    try:
        await future
    except:
        (type, value, traceback) = sys.exc_info()
        assert (type is not None and value is not None and traceback is not None)
        _on_uncaught_exception(type, value, traceback)


def _on_uncaught_exception(type_: Type[BaseException], value: BaseException, traceback: TracebackType) -> None:
    exception_msg = ''.join(_traceback.format_exception_only(type_, value))
    full_traceback_msg = ''.join(_traceback.format_exception(
        type_, value, traceback, chain=True))
    print(exception_msg + "\n" + full_traceback_msg, file=sys.stderr)
    if asyncio.get_event_loop().is_running():
        QMessageBox.critical(None, "Error", exception_msg +
                                "\n" + full_traceback_msg)
