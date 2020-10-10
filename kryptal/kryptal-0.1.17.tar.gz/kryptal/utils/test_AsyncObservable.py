from kryptal.utils.AsyncObservable import AsyncObservable, ListenerHandle
from kryptal.testutils.ApplicationHelpers import async_unit
import unittest
from unittest.mock import AsyncMock


class test_AsyncObservable(unittest.TestCase):
    @async_unit
    async def test_givenEmptyObservable_whenCalled_thenDoesntCrash(self) -> None:
        observable = AsyncObservable()
        await observable.call()

    @async_unit
    async def test_givenOneCallback_whenCalled_thenCallsCallback(self) -> None:
        observable = AsyncObservable()
        callback = AsyncMock()
        observable.add(callback)
        await observable.call()
        callback.assert_called_once_with()

    @async_unit
    async def test_givenTwoCallbacks_whenCalled_thenCallsBothCallbacks(self) -> None:
        observable = AsyncObservable()
        callback1 = AsyncMock()
        callback2 = AsyncMock()
        observable.add(callback1)
        observable.add(callback2)
        await observable.call()
        callback1.assert_called_once_with()
        callback2.assert_called_once_with()

    @async_unit
    async def test_givenOneCallback_whenRemoved_thenIsNotCalled(self) -> None:
        observable = AsyncObservable()
        callback = AsyncMock()
        handle = observable.add(callback)
        observable.remove(handle)
        await observable.call()
        callback.assert_not_called()

    @async_unit
    async def test_givenTwoCallbacks_whenFirstRemoved_thenCallsOnlySecond(self) -> None:
        observable = AsyncObservable()
        callback1 = AsyncMock()
        callback2 = AsyncMock()
        handle1 = observable.add(callback1)
        handle2 = observable.add(callback2)
        observable.remove(handle1)
        await observable.call()
        callback1.assert_not_called()
        callback2.assert_called_once_with()

    @async_unit
    async def test_givenTwoCallbacks_whenSecondRemoved_thenCallsOnlyFirst(self) -> None:
        observable = AsyncObservable()
        callback1 = AsyncMock()
        callback2 = AsyncMock()
        handle1 = observable.add(callback1)
        handle2 = observable.add(callback2)
        observable.remove(handle2)
        await observable.call()
        callback1.assert_called_once_with()
        callback2.assert_not_called()

    @async_unit
    async def test_givenTwoCallbacks_whenBothRemoved_thenCallsNone(self) -> None:
        observable = AsyncObservable()
        callback1 = AsyncMock()
        callback2 = AsyncMock()
        handle1 = observable.add(callback1)
        handle2 = observable.add(callback2)
        observable.remove(handle1)
        observable.remove(handle2)
        await observable.call()
        callback1.assert_not_called()
        callback2.assert_not_called()

    @async_unit
    async def test_givenOneCallback_whenCalledTwice_thenIsCalledTwice(self) -> None:
        observable = AsyncObservable()
        callback = AsyncMock()
        observable.add(callback)
        await observable.call()
        await observable.call()
        self.assertEqual(2, callback.call_count)
