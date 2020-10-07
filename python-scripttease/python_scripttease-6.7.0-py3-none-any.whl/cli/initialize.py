# Imports

from commonkit import smart_cast
from configparser import ConfigParser
import logging
import os
from ..constants import LOGGER_NAME

log = logging.getLogger(LOGGER_NAME)

# Exports

__all__ = (
    "context_from_cli",
    "filters_from_cli",
    "options_from_cli",
    "variables_from_file",
)

# Functions


def context_from_cli(variables):
    """Takes a list of variables given in the form of ``name:value`` and converts them to a dictionary.

    :param variables: A list of strings of ``name:value`` pairs.
    :type variables: list[str]

    :rtype: dict

    The ``value`` of the pair passes through "smart casting" to convert it to the appropriate Python data type.

    """
    context = dict()
    for i in variables:
        key, value = i.split(":")
        context[key] = smart_cast(value)

    return context


def filters_from_cli(filters):
    """Takes a list of filters given in the form of ``name:value`` and converts them to a dictionary.

    :param filters: A list of strings of ``attribute:value`` pairs.
    :type filters: list[str]

    :rtype: dict

    """
    _filters = dict()
    for i in filters:
        key, value = i.split(":")
        if key not in filters:
            _filters[key] = list()

        _filters[key].append(value)

    return _filters


def options_from_cli(options):
    """Takes a list of variables given in the form of ``name:value`` and converts them to a dictionary.

    :param options: A list of strings of ``name:value`` pairs.
    :type options: list[str]

    :rtype: dict

    The ``value`` of the pair passes through "smart casting" to convert it to the appropriate Python data type.

    """
    _options = dict()
    for i in options:
        key, value = i.split(":")
        _options[key] = smart_cast(value)

    return _options


def variables_from_file(path):
    """Loads variables from a given INI file.

    :param path: The path to the INI file.
    :type path: str

    :rtype: dict | None

    The resulting dictionary flattens the sections and values. For example:

    .. code-block:: ini

        [copyright]
        name = ACME, Inc.
        year = 2020

        [domain]
        name = example.com
        tld = example_com

    The dictionary would contain:

    .. code-block:: python

        {
            'copyright_name': "ACME, Inc.",
            'copyright_year': 2020,
            'domain_name': "example.com",
            'domain_tld': "example_com",
        }

    """
    if not os.path.exists(path):
        log.warning("Variables file does not exist: %s" % path)
        return None

    ini = ConfigParser()
    ini.read(path)

    variables = dict()
    for section in ini.sections():
        for key, value in ini.items(section):
            key = "%s_%s" % (section, key)
            variables[key] = smart_cast(value)

    return variables
