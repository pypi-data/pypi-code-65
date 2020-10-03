import importlib
import os
import lazy_object_proxy

__version__ = '0.0.4'
ENVIRONMENT_VARIABLE = 'SANIC_SETTINGS_MODULE'


def load_settings():
    settings = {}

    settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
    if not settings_module:
        raise RuntimeError(
            "You must define the environment variable %s before "
            "accessing settings." % ENVIRONMENT_VARIABLE
        )

    module = importlib.import_module(settings_module)
    return {
        key: getattr(module, key)
        for key in dir(module)
        if key.isupper()
    }


settings = lazy_object_proxy.Proxy(load_settings)
