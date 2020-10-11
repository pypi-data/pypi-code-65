from kryptal.testutils.Async import waitForConditionWithTimeout, ensureConditionInTimeout
from kryptal.testutils.ApplicationHelpers import with_app_async
import kryptal.gui.TaskManager as TaskManager
import asyncio
import unittest


class test_TaskManager(unittest.TestCase):
    @with_app_async
    async def test_create_task(self) -> None:
        var = []

        async def func() -> None:
            await asyncio.sleep(0.1)
            print("finished\n")
            var.append(5)

        task = TaskManager.create_task(func())
        # assert it gets done, even without awaiting it
        await waitForConditionWithTimeout(task.done, timeout=1)
        self.assertEqual([5], var, "assert task result is correct")
