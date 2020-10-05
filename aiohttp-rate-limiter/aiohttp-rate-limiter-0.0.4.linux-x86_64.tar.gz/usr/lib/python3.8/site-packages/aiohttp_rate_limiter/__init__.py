from typing import Dict, Any, Callable

from aiohttp.web import Application, HTTPTooManyRequests

from .cfg import Config

from .limiters import methods


async def default_error(request):
    return HTTPTooManyRequests()


def setup(app: Application, error_handler: Callable = default_error,
          config: Config = None, **params: Dict[str, Any]) -> None:
    if type(config) == Config:
        method = config.__dict__.get('method')
    elif config is not None:
        raise TypeError('Config should be a Config object')
    else:
        method = params.get('method')
        config = Config(**params)

    if method:
        limiter = method.value(config, error_handler)
        app.middlewares.insert(0, limiter.handle)
    else:
        raise KeyError('The main parameter "method" is missing')
