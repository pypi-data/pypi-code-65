import os
import dtool_lookup_server_plugin_scaffolding

from . import __version__

class Config(object):
    SOME_SENSITIVE_PLUGIN_SPECIFIC_SETTING = os.environ.get('DTOOL_LOOKUP_SERVER_PLUGIN_SCAFFOLDING_SOME_SENSITIVE_PLUGIN_SPECIFIC_SETTING', 'secret')
    SOME_PUBLIC_PLUGIN_SPECIFIC_SETTING = os.environ.get('DTOOL_LOOKUP_SERVER_PLUGIN_SCAFFOLDING_SOME_PUBLIC_PLUGIN_SPECIFIC_SETTING', 'public')

    @classmethod
    def to_dict(cls):
        """Convert plugin configuration into dict."""
        exclusions = [
            'SOME_SENSITIVE_PLUGIN_SPECIFIC_SETTING',
        ]  # config keys to exclude
        d = {'version': __version__}
        for k, v in cls.__dict__.items():
            # select only capitalized fields
            if k.upper() == k and k not in exclusions:
                d[k.lower()] = v
        return d
