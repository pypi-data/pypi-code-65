from typing import NewType, Callable, Awaitable, Dict
import asyncio
from typing_extensions import final


ListenerHandle = NewType("ListenerHandle", int)


@final
class AsyncObservable:
    def __init__(self) -> None:
        self._listeners: Dict[ListenerHandle,
                              Callable[[], Awaitable[None]]] = {}
        self._counter = 0

    def add(self, listener: Callable[[], Awaitable[None]]) -> ListenerHandle:
        handle = ListenerHandle(self._counter)
        self._counter = self._counter + 1
        self._listeners[handle] = listener
        return handle

    def remove(self, handle: ListenerHandle) -> None:
        del self._listeners[handle]

    async def call(self) -> None:
        await asyncio.gather(*[func() for _, func in self._listeners.items()])
