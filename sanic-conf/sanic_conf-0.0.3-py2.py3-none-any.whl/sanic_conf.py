import importlib
import os

__version__ = '0.0.3'
ENVIRONMENT_VARIABLE = 'SANIC_SETTINGS_MODULE'


class Settings:
    def __init__(self):
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            raise RuntimeError(
                "You must define the environment variable %s before "
                "accessing settings." % ENVIRONMENT_VARIABLE
            )

        module = importlib.import_module(settings_module)

        for setting in dir(module):
            if setting.isupper():
                setting_value = getattr(module, setting)
                setattr(self, setting, setting_value)


settings = Settings()
