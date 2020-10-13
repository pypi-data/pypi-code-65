import os
import json
from pydoc import locate
from applipy import Application, Config
from applipy_inject import Injector
from applipy.application.application import (
    BindFunction,
    ModuleManager,
    RegisterFunction,
)
from logging import Logger, getLevelName, ERROR

try:
    import yaml
except ImportError:
    yaml = None


class LoadFromConfigModuleManager(ModuleManager):

    def set_application(self, app: Application) -> None:
        self.app = app

    def configure_all(self, bind_function: BindFunction,
                      register_function: RegisterFunction) -> None:
        config = self.injector.get(Config)

        module_names = config.get('app.modules')
        if module_names:
            for module, name in ((locate(name), name) for name in module_names):
                if module:
                    self.app.install(module)
                else:
                    self._log(ERROR, f'Could not load module `{name}`')
                    raise ImportError(name)

        super().configure_all(bind_function, register_function)

    def _log(self, level, *args, **kwargs):
        try:
            self.injector.get(Logger).log(level, *args, **kwargs)
        except Exception:
            print(f"[{getLevelName(level)}]", *args)


def load_config_from_json(config_path):
    config_file = os.path.join(config_path, f'{env.lower()}.json')
    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    return config


def load_config_from_yaml(config_path):
    config_file = os.path.join(config_path, f'{env.lower()}.yaml')
    if yaml and os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.Loader)
    else:
        config = {}
    return config


def load_config(config_path, env):
    config = {}
    config.update(load_config_from_yaml(config_path))
    config.update(load_config_from_json(config_path))

    protocols = []
    provider_names = Config(config, []).get('config.protocols')
    if provider_names:
        for provider, name in ((locate(name), name) for name in provider_names):
            if provider:
                print(f'Adding configuration provider `{name}`')
                protocols.append(provider())
            else:
                print(f'[ERROR] Could not load configuration provider `{name}`')
                raise ImportError(name)

    return Config(config, protocols)


def main(config_path, env):
    injector = Injector()
    module_manager = LoadFromConfigModuleManager(injector)
    app = Application(load_config(config_path, env),
                      injector=injector,
                      module_manager=module_manager)
    module_manager.set_application(app)
    app.run()


if __name__ == '__main__':
    config_path = os.environ.get('APPLIPY_CONFIG_PATH', os.path.curdir)
    env = os.environ.get('APPLIPY_ENV', 'DEV')
    main(config_path, env)
