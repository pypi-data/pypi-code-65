"""All type annotations go here."""

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from aio_wx_widgets.core.binding import Binding

    from aio_wx_widgets.controller import BaseController
    from asyncio import AbstractEventLoop

    try:
        import Protocol  # type: ignore
    except ImportError:
        from typing_extensions import Protocol

    assert BaseController
    assert AbstractEventLoop
    assert Binding

    class Choice(Protocol):
        """Typing protocol to be used for static type checking."""

        label: str
        value: Any
