#!/usr/bin/env python3

import os
import io
import sys

from core.utils.dicts import DotNotation as DotNotation
import core.utils.yaml as yaml
import core.utils.json as json

class SessionsManager(object):
    """ Beer Sessions Manager Class

    Read Session Yaml file in 
    - ~/include-beer-sessions.yml
    or
    - ENV INCLUDE_BEER_SESSION_FILE (takes precedents)

    Provides object of sessions in yaml file


    """

    def __init__(self, session_file=None):
        self.sessions = {}
        

        # If env INCLUDE_BEER_SESSION_FILE is set, always use that
        # elif try ~/include-beer.cfg
        # else return empty dict
        _expanded_user_file = os.path.expanduser('~/include-beer-sessions.yml')
        if os.getenv('INCLUDE_BEER_SESSION_FILE', 0):
            _env_file = os.environ['INCLUDE_BEER_SESSION_FILE']
            if os.path.exists(_env_file):
                self.session_file = _env_file
                self._use_session_file = True
        elif os.path.exists(_expanded_user_file):
            self.session_file = _expanded_user_file
            self._use_session_file = True
        else:
            self._use_session_file = False

        if self._use_session_file:

            # Load in our session yaml file
            self.sessions = yaml.yaml_loader(self.session_file)

    def session(self, dict):
        """ Return supplied session (as dict) as json object dot notated

        Required:
        dict (dict): dict of session

        """
        return json.DotNotation(dict)
