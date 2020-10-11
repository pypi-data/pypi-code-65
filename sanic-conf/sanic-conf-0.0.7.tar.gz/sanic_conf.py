import importlib
import os

__version__ = '0.0.7'


class Settings:
    ENVIRONMENT_VARIABLE = 'SANIC_SETTINGS_MODULE'

    def __init__(self):
        self.__ready = False

    def __getattr__(self, item):
        if self.__ready is False:
            self._setup()

        if item in self.__dict__:
            return self.__dict__[item]
        raise AttributeError(item)

    def __contains__(self, item):
        if self.__ready is False:
            self._setup()
        return item in self.__dict__

    def _setup(self):
        if self.__ready:
            raise RuntimeError("_setup() isn't reentrant")

        settings_module = os.environ.get(self.ENVIRONMENT_VARIABLE)
        if not settings_module:
            raise RuntimeError(
                "You must define the environment variable %s before "
                "accessing settings." % self.ENVIRONMENT_VARIABLE
            )

        self._load_settings(settings_module)
        self.__ready = True

    def _load_settings(self, module_path):
        module = importlib.import_module(module_path)
        self._extend(module)

    def _extend(self, module):
        self.__dict__.update({
            key: getattr(module, key)
            for key in dir(module)
            if key.isupper()
        })


settings = Settings()
