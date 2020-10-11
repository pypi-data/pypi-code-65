import asyncio
import sys
from typing import Callable, Awaitable, Any, Optional
from types import TracebackType
from functools import wraps
from asyncqt import QEventLoop  # type: ignore
from kryptal.gui import Application


def with_app_async(func: Callable[..., Awaitable[None]]) -> Callable[..., None]:
    Application.create_test_instance()
    app = Application.get_instance()

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        app.run_for_test(func(*args, **kwargs))

    return wrapper


def with_app(func: Callable[..., None]) -> Callable[..., None]:
    Application.create_test_instance()
    app = Application.get_instance()

    async def async_wrapper(*args: Any, **kwargs: Any) -> None:
        func(*args, **kwargs)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        app.run_for_test(async_wrapper(*args, **kwargs))

    return wrapper


def async_unit(func: Callable[..., Awaitable[None]]) -> Callable[..., None]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        future = func(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper
