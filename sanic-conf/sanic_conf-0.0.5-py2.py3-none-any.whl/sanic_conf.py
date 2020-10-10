import importlib
import os

__version__ = '0.0.5'
ENVIRONMENT_VARIABLE = 'SANIC_SETTINGS_MODULE'


class Settings:
    def __init__(self):
        self.__ready = False

    def __getattr__(self, item):
        if self.__ready is False:
            self.__setup()

        if item in self.__dict__:
            return self.__dict__[item]
        raise AttributeError(item)

    def __contains__(self, item):
        if self.__ready is False:
            self.__setup()
        return item in self.__dict__

    def __setup(self):
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            raise RuntimeError(
                "You must define the environment variable %s before "
                "accessing settings." % ENVIRONMENT_VARIABLE
            )

        module = importlib.import_module(settings_module)
        self.__dict__.update({
            key: getattr(module, key)
            for key in dir(module)
            if key.isupper()
        })
        self.__ready = True


settings = Settings()
