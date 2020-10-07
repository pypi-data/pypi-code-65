# -*- coding: utf-8 -*-

import asyncio
import threading
import time
import functools
from . import app

class Processor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._loop = None

    def run(self):
        self._loop = asyncio.new_event_loop()
        self._loop.run_forever()

    def post_task(self, callback):
        self._loop.call_soon_threadsafe(
            functools.partial(self._do_callback, callback))

    def start(self):
        super().start()

        while self._loop is None:
            time.sleep(0.001)

    def stop(self):
        self._loop.call_soon_threadsafe(self._do_stop)
        super().join()

    def _do_stop(self):
        self._loop.stop()

    def _do_callback(self, callback):
        try:
            callback()
        except Exception as e:
            app.logger.error('处理任务发生异常', exc_info=True)

def task():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            app.processor.post_task(functools.partial(func, *args, **kwargs))
        return wrapper
    return decorator
