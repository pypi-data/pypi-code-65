# Imports

from commonkit import any_list_item
import logging
from ..constants import LOGGER_NAME
from .ini import Config

log = logging.getLogger(LOGGER_NAME)

# Exports

__all__ = (
    "filter_commands",
    "load_commands",
)

# Functions


def filter_commands(commands, environments=None, tags=None):
    """Filter commands based on the given criteria. 
    
    :param commands: The commands to be filtered.
    :type commands: list
    
    :param environments: Environment names to be matched.
    :type environments: list[str]
     
    :param tags: Tag names to be matched.
    :type tags: list[str]

    """
    filtered = list()
    for command in commands:
        if environments is not None:
            if not any_list_item(environments, command.environments):
                continue
        
        if tags is not None:
            if not any_list_item(tags, command.tags):
                continue
        
        filtered.append(command)
        
    return filtered


def load_commands(path, filters=None, overlay="ubuntu", **kwargs):
    """Load commands from a configuration file.

    :param path: The path to the configuration file.
    :type path: str

    :param filters: Used to filter commands.
    :type filters: dict

    :param overlay: The name of the command overlay to apply to generated commands.
    :type overlay: str

    :rtype: list[scriptetease.library.commands.base.Command] | scriptetease.library.commands.base.ItemizedCommand] |
            None

    :returns: A list of command instances or ``None`` if the configuration could not be loaded.

    kwargs are passed to the configuration class for instantiation.

    """
    _config = load_config(path, overlay, **kwargs)
    if _config is None:
        return None

    commands = _config.get_commands()

    if filters is not None:
        criteria = dict()
        for attribute, values in filters.items():
            criteria[attribute] = values

        commands = filter_commands(commands, **criteria)

    return commands


def load_config(path, overlay="ubuntu", **kwargs):
    """Load a command configuration.

    :param path: The path to the configuration file.
    :type path: str

    :param overlay: The name of the command overlay to apply to generated commands.
    :type overlay: str

    :rtype: Config | None

    kwargs are passed to the configuration class for instantiation.

    """
    if path.endswith(".ini"):
        _config = Config(path, overlay=overlay, **kwargs)
    # elif path.endswith(".yml"):
    #     _config = YAML(path, **kwargs)
    else:
        log.warning("Input file format is not currently supported: %s" % path)
        return None

    if not _config.load():
        log.error("Failed to load config file: %s" % path)
        return None

    return _config
