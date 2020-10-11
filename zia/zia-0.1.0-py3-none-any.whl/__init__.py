import logging
import logging.config
import os
import pkgutil
import sys

import yaml

USER_CONFIG_FILE = './config.yaml'

def load_config():
    global _CONFIG
    _CONFIG = yaml.safe_load(pkgutil.get_data(__package__, 'data/config.yaml').decode('utf-8'))
    if os.path.exists(USER_CONFIG_FILE):
        with open(USER_CONFIG_FILE) as configfile:
            _CONFIG = yaml.safe_load(configfile.read())
    if 'log' in _CONFIG:
        logging.config.dictConfig(_CONFIG['log'])

def get_config():
    if _CONFIG is None:
        load_config()
    return _CONFIG

LOGGER = logging.getLogger(__name__)
_CONFIG = None
