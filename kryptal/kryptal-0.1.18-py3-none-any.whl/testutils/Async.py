import asyncio
from typing import Awaitable, Tuple, Set, Callable, Any
from asyncio.futures import Future


class AsyncCallbackMock:
    def __init__(self) -> None:
        self._callEvent = asyncio.Event()

    async def call(self) -> None:
        self._callEvent.set()

    async def expect_call(self, timeout: float) -> None:
        waiter: Awaitable[Any] = self._callEvent.wait()
        done: Set[Future[Any]]
        pending: Set[Future[Any]]
        done, pending = await asyncio.wait([waiter], timeout=timeout)
        assert(len(done)+len(pending) == 1)
        assert len(done) == 1, "AsyncCallbackMock.expect_call: Callback was not called"
        self._callEvent = asyncio.Event()

    async def expect_doesnt_call(self, timeout: float) -> None:
        waiter: Awaitable[Any] = self._callEvent.wait()
        done: Set[Future[Any]]
        pending: Set[Future[Any]]
        done, pending = await asyncio.wait([waiter], timeout=timeout)
        assert(len(done)+len(pending) == 1)
        assert len(done) == 0, "AsyncCallbackMock.expect_doesnt_call: Callback was called"
        for p in pending:
            p.cancel()
        self._callEvent = asyncio.Event()


async def waitForCondition(condition: Callable[[], bool]) -> None:
    while not condition():
        await asyncio.sleep(0.1)


async def waitForConditionWithTimeout(condition: Callable[[], bool], timeout: float) -> None:
    try:
        cond_waiter = waitForCondition(condition)
        await asyncio.wait_for(cond_waiter, timeout=timeout)
    except asyncio.TimeoutError:
        assert False, "Condition didn't occur before timeout"


async def ensureConditionInTimeout(condition: Callable[[], bool], timeout: float) -> None:
    await asyncio.sleep(timeout)
    assert condition(), "Condition didn't stay true during timeout"
