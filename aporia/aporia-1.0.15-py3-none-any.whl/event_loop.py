import asyncio
from concurrent.futures import ALL_COMPLETED, Future, wait
import logging
from threading import Thread
from typing import Any, Coroutine, Optional, Set

from aporia.consts import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class EventLoop:
    """Asyncio event loop manager for worker thread loop."""

    def __init__(self):
        """Initializes an EventLoop instance."""
        logger.debug("Starting event loop in a worker thread.")
        self.loop = asyncio.new_event_loop()
        self.loop_thread = Thread(target=self.run_loop, daemon=True)

        # We keep a list of all tasks that were not awaited, to allow flushing
        # We have to do this manually to support python versions below
        # 3.7 (otherwise we could use asyncio.all_tasks())
        self.futures = []

        self.loop_thread.start()

    def run_loop(self):
        """Runs the asyncio event loop."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_coroutine(self, coro: Coroutine, await_result: Optional[bool] = True) -> Optional[Any]:
        """Runs a coroutine in the worker thread loop.

        Args:
            coro (Coroutine): Coroutine to execute
            await_result (bool, optional): If await_result is True, this will block untill the
                coroutine finishes executing. Defaults to True.

        Returns:
            Optional[Any]: Coroutine return value, if await_result is True
        """
        future = asyncio.run_coroutine_threadsafe(coro=coro, loop=self.loop)

        if await_result:
            return future.result()
        else:
            self.futures.append(future)
            return None

    def flush(self, timeout: Optional[int] = None) -> Set[Future]:
        """Waits for all currently scheduled tasks to finish.

        Args:
            timeout (int, optional): Maximum number of seconds to wait for tasks to
                complete. Default to None.

        Returns:
            Set[Future]: Set of tasks that were not completed after the timeout.
        """
        futures = self.futures
        self.futures = []

        logger.debug("Waiting for {} scheduled tasks to finish executing.".format(len(futures)))
        done, not_done = wait(futures, timeout=timeout, return_when=ALL_COMPLETED)

        logger.debug("{} tasks finished, {} tasks not finished.".format(len(done), len(not_done)))
        self.futures.extend(not_done)

        return not_done
