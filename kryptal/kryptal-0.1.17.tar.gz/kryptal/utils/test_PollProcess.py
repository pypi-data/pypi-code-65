from kryptal.utils.PollProcess import PollProcess
from kryptal.testutils.ApplicationHelpers import with_app_async
from kryptal.testutils.Async import AsyncCallbackMock
import unittest


class test_PollProcess(unittest.TestCase):
    @with_app_async
    async def test_givenFastprocess_whenPolled_thenCallsCallback(self) -> None:
        callback = AsyncCallbackMock()
        p = PollProcess('/bin/bash', '-c', 'echo')
        p.addListener(callback.call)
        p.start()
        await callback.expect_call(timeout=1)

    @with_app_async
    async def test_givenFastprocess_whenNotPolled_thenDoesnCallCallback(self) -> None:
        callback = AsyncCallbackMock()
        p = PollProcess('/bin/bash', '-c', 'echo')
        p.addListener(callback.call)
        # don't call p.start()
        await callback.expect_doesnt_call(timeout=1)

    @with_app_async
    async def test_givenSlowprocess_whenPolled_thenCallsOnlyWhenFinished(self) -> None:
        callback = AsyncCallbackMock()
        p = PollProcess('/bin/bash', '-c', 'sleep 1')
        p.addListener(callback.call)
        p.start()
        await callback.expect_doesnt_call(timeout=0.75)
        await callback.expect_call(timeout=0.5)

    @with_app_async
    async def test_poll_reruns_process(self) -> None:
        callback = AsyncCallbackMock()
        p = PollProcess('/bin/bash', '-c', 'sleep 1')
        p.addListener(callback.call)
        p.start()
        await callback.expect_doesnt_call(timeout=0.75)
        await callback.expect_call(timeout=0.5)
        await callback.expect_doesnt_call(timeout=0.5)
        await callback.expect_call(timeout=0.75)
