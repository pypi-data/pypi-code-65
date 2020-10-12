import os
import yaml
import configparser
import logging

_config = {}
_config_files = []
_config_sources = []

"""
this is really simple 
1. set config directory
2. load_config()
3. refresh_config_files() if new files in config dir
4. reload_config()

you can reference text files and ENV values in your yaml config
---
key1: !text_file /path/file.txt
key2: !env PATH
"""


class Loader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def text_file_loader(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return f.read()

    def environ_loader(self, node):
        return os.environ.get(self.construct_scalar(node), None)

    def yaml_loader(self, node):
        node_info = self.construct_scalar(node).split(' ')
        filename = os.path.join(self._root, node_info[0])
        with open(filename, 'r') as f:
            inc_yaml = yaml.load(f, Loader)
            if node_info[1] is None:
                return inc_yaml
            else:
                return _get(node_info[1], None, inc_yaml)

    def ini_loader(self, node):
        node_info = self.construct_scalar(node).split(' ')
        filename = os.path.join(self._root, node_info[0])
        with open(filename, 'r') as f:
            config = configparser.ConfigParser(allow_no_value=True)
            try:
                config.read_file(f)
                if len(node_info) == 3:
                    return config[node_info[1]][node_info[2]]
                if len(node_info) == 2:
                    entries = {}
                    for key, value in config.items(node_info[1]):
                        entries[key] = value
                    return entries
                return None
            except Exception as e:
                logging.warning(str(e))
                return None


Loader.add_constructor('!text_file', Loader.text_file_loader)
Loader.add_constructor('!env', Loader.environ_loader)
Loader.add_constructor('!yaml', Loader.yaml_loader)
Loader.add_constructor('!ini', Loader.ini_loader)


def refresh_config_files():
    global _config_sources, _config_files
    _config_files_ = []
    for cfg_source in _config_sources:
        if os.path.isdir(cfg_source):
            for f in [f for f in os.listdir(cfg_source)
                      if os.path.isfile(os.path.join(cfg_source, f)) and (f.endswith('.yaml') or f.endswith('.yml'))]:
                _config_files_.append(os.path.join(cfg_source, f))
        if os.path.isfile(cfg_source):
            _config_files_.append(cfg_source)
    _config_files = _config_files_


def reload_config():
    global _config_files, _config
    _config_ = {}
    refresh_config_files()
    for cfg_file in _config_files:
        try:
            with open(cfg_file, 'r') as fh:
                _config__ = yaml.load(fh, Loader)
                _config_ = {**_config__, **_config_}
        except yaml.YAMLError as e:
            print(f'YAML error {e}')
        except IOError as e:
            print(f'sth IO {e}')
    _config = _config_


def load_config():
    reload_config()


def _get(key, default, source):
    """Get config value from config by key. can access nested keys with '.' seperator"""
    result = source
    for keyPathElement in key.split('.'):
        if type(result) is not dict:
            result = default
            break
        result = result.get(keyPathElement, default)
    return result


def get(key, default=None):
    """Get config value from config by key. can access nested keys with '.' seperator"""
    global _config
    return _get(key, default, _config)


def get_config_sources_from_args(cli_args):
    global _config_sources
    __config_sources = []
    if cli_args.config_dir is not None:
        for config_dir in cli_args.config_dir:
            __config_sources.append(config_dir)
    if cli_args.config_file is not None:
        for config_file in cli_args.config_file:
            __config_sources.append(config_file)
    _config_sources = __config_sources


def get_config_sources_from_environ(environ_name: str):
    global _config_sources
    _config_sources = [os.environ.get(environ_name)]


def set_config_sources(sources):
    global _config_sources
    _config_sources = sources
