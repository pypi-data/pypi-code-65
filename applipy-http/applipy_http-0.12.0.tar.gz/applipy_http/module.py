import logging

from aiohttp import web

from applipy import Config, LoggingModule, Module
from applipy_inject import with_names
from applipy_http.config import ServerConfig
from applipy_http.server import HttpServer


def _app_runner_wrapper(
        app: web.Application,
        logger: logging.Logger
) -> web.AppRunner:
    return web.AppRunner(app, logger=logger)


def _aiohttp_application_builder() -> web.Application:
    return web.Application()


class HttpModule(Module):

    def __init__(self, config: Config):
        self.config = config

    def configure(self, bind, register):
        webapp_names = self._get_webapp_names()

        for name in webapp_names:
            host = self._get_property(name, 'host')
            port = self._get_property(name, 'port')
            bind(_aiohttp_application_builder, name=name)
            bind(web.AppRunner,
                 with_names(_app_runner_wrapper, {'app': name}),
                 name=name)
            bind(ServerConfig, ServerConfig(name, host, port), name=name)

            register(with_names(HttpServer, {'app_runner': name,
                                             'apis': name,
                                             'config': name}))

    def _get_webapp_names(self):
        names = set()
        for key in self.config.keys():
            if key.startswith('http.'):
                parts = key.split('.')
                if len(parts) == 3:
                    names.add(parts[1])
                elif len(parts) == 2:
                    names.add(None)

        return names

    def _get_property(self, name, prop):
        if name is None:
            infix = ''
        else:
            infix = f'.{name}'
        return self.config.get(f'http{infix}.{prop}')

    @classmethod
    def depends_on(cls):
        return LoggingModule,
