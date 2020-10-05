from typing import Callable
from asyncio import get_event_loop, sleep

from aiohttp.web import middleware

from ..cfg import Config


class SlidingLog:
    def __init__(self, config: Config, error_handler: Callable):
        self._config: Config = config

        self._clients = {}

        self._error_handler: Callable = error_handler

        self._check_typing()
        self._set_interval()

    def _check_typing(self):
        cfg = self._config
        assert type(cfg.max_requests) == int
        assert type(cfg.interval) == int

    def _set_interval(self):
        async def clear_count(self):
            while True:
                self._clients = {}
                await sleep(self._config.interval)

        loop = get_event_loop()
        loop.create_task(clear_count(self))

    @middleware
    async def handle(self, request, handler):
        ip = request.remote
        count = self._clients.get(ip, 0)

        if not count:
            self._clients[ip] = 0

        if count < self._config.max_requests:
            self._clients[ip] += 1
            return await handler(request)
        else:
            return await self._error_handler(request)
