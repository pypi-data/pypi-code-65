from functools import wraps
from asyncio import ensure_future
from typing import Callable, Any, Coroutine
import logging, sys
import kryptal.gui.TaskManager as TaskManager


# TODO Test:
# - slot is called
# - error is not silently ignored
def async_slot(func: Callable[..., Coroutine[None, None, None]]) -> Callable[..., None]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        TaskManager.create_task(func(*args, **kwargs))
    return wrapper
