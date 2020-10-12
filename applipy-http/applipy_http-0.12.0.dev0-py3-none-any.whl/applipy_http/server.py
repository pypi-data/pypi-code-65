import logging
from asyncio import sleep
from typing import Any, List

import aiohttp_cors
from aiohttp import web

from applipy import AppHandle
from applipy_http.api import Api
from applipy_http.config import ServerConfig
from applipy_http.endpoint import EndpointMethod
from applipy_http.types import Context


def _adapt_handler(func: EndpointMethod, ctx: Context) -> Any:
    async def wrapper(request: web.Request) -> web.StreamResponse:
        return await func(request, ctx)

    return wrapper


class HttpServer(AppHandle):

    def __init__(self, app_runner: web.AppRunner,
                 apis: List[Api],
                 config: ServerConfig,
                 logger: logging.Logger):
        self.runner = app_runner
        self.apis = apis
        self.name = config.name
        self.host = config.host
        self.port = config.port
        self.logger = logger

    async def on_init(self):
        cors = aiohttp_cors.setup(self.runner.app)

        for api in self.apis:
            for route_def in api.get_routes():
                handler = route_def.handler

                route = self.runner.app.router.add_route(
                    route_def.method,
                    route_def.path,
                    _adapt_handler(handler, {})
                )

                if route_def.cors_config:
                    cors.add(route, route_def.cors_config)

    async def on_start(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        self.logger.info(
            'HTTP server' + (f' `{self.name}` ' if self.name else ' ') + 'started at http://%s:%s',
            self.host,
            self.port
        )
        while True:
            await sleep(3600)

    async def on_shutdown(self):
        self.logger.info('Shutting down HTTP server' + (f' `{self.name}`' if self.name else ''))
        await self.runner.cleanup()
