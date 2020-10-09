#!/usr/bin/env python3

import os
import io
import sys
import configparser

from core.utils.dicts import DotNotation as DotNotation
import core.utils.yaml as yaml
import core.utils.json as json

class ConfigManager(object):
    """ Configuration Manager Class

    Reads all configuration files
    - defaults.yml
    - ~/include-beer.yml
    - ENV INCLUDE_BEER_CONFIG

    Set configuration values based on order of precedents (lowest to highest)
    - defaults.yml
    - specified config file (~/beer/include-beer.yml or ENV INCLUDE_BEER_CONFIG)
    - Environmental overrides

    """

    def __init__(self, cfg_file=None, defaults_file=None):
        self._defaults = {}
        self._base_config_def = {}
        self._option_type_def = {}
        self.config_file = ''
        self._config_file_def = {}
        self._env_config_def = {}
        self.operating_dict = {}

        # Load in our default value yaml file
        self._defaults = yaml.yaml_loader(defaults_file or ('%s/defaults.yml' % os.path.dirname(__file__)))

        # Load a configuration file definition if defined
        # if env INCLUDE_BEER_CONFIG is set, always use that
        # elif try ~/include-beer.yml
        # else use base config defaults
        _expanded_user_config = os.path.expanduser('~/include-beer.yml')
        if os.getenv('INCLUDE_BEER_CONFIG', 0):
            _env_config_file = os.environ['INCLUDE_BEER_CONFIG']
            if os.path.exists(_env_config_file):
                self.config_file = _env_config_file
                self._use_config_file = True
        elif os.path.exists(_expanded_user_config):
            self.config_file = _expanded_user_config
            self._use_config_file = True
        else:
            self._use_config_file = False

        if self._use_config_file:
            self._config_file_def = yaml.yaml_loader(self.config_file)

        self.operating_dict.update(self._defaults)
        self.operating_dict.update(self._config_file_def)
        for _k, _v in self.operating_dict.items():
            setattr(self, _k, self.dot(_v))



    def dot(self, dict):
        """ Return supplied session (as dict) as json object dot notated

        Required:
        dict (dict): dict of session

        """
        return json.DotNotation(dict)

