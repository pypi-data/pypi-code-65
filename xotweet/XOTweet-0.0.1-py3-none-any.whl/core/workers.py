#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class TaskExecuter:
    def __init__(self, threads):
        self.pool = ThreadPoolExecutor(threads)
        self.results = []
        self.tasks = []

    async def execute_task(self, func, **kwargs):
        future = self.pool.submit(func, **kwargs)
        awaitable = asyncio.wrap_future(future)
        return await awaitable

    def add_task(self, func):
        self.tasks.append(func)

    async def app(self):
        result = await asyncio.gather(*self.tasks)
        self.results.append(result)
