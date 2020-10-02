from pathlib import Path
import yaml
from addict import Dict
from .utils import more_yaml

__version__ = '1.1'

class Config(object):
    def __init__(self, cfg=None, filename=None):
        super().__setattr__('_cfg', Dict(cfg))
        super().__setattr__('_cfg_filename', filename)

    @staticmethod
    def from_file(file_path):
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            log_info = '{} not exist'.format(file_path.as_posix())
            raise IOError(log_info)

        # Yaml
        if file_path.suffix == '.yaml':
            with file_path.open('r', encoding='utf-8') as f:
                cfg_dict = yaml.load(f, Loader=yaml.FullLoader)
            return Config(cfg=cfg_dict, filename=file_path.name)
        else:
            raise IOError('Not support file suffix yet.')

    def __getitem__(self, name):
        return self._cfg.get(name)

    def __setitem__(self, name, value):
        self._cfg[name] = value

    def __getattr__(self, name):
        return self._cfg.get(name)

    def __setattr__(self, name, value):
        self._cfg[name] = value

    def __iter__(self):
        return iter(self._cfg)

    def __repr__(self):
        return self._cfg.__repr__()
