# Imports

import logging
from importlib import import_module
from .constants import LOGGER_NAME
from .library.commands import ItemizedCommand

log = logging.getLogger(LOGGER_NAME)

# Exports

__all__ = (
    "Factory",
)

# Classes


class Factory(object):
    """A command factory."""

    def __init__(self, overlay):
        """Initialize the factory.

        :param overlay: The name of the overlay to use for generating commands.
        :type overlay: str

        """
        self.is_loaded = False
        self.overlay = None
        self._overlay = overlay

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self._overlay)

    def get_command(self, name, *args, **kwargs):
        """Get a command.

        :param name: The name of the command.
        :type name: str

        args and kwargs are passed to the initialize the command.

        :rtype: scripttease.library.commands.Command | scripttease.library.commands.ItemizedCommand

        :raise: RuntimeError
        :raises: ``RuntimeError`` if the factory has not yet been loaded.

        """
        if not self.is_loaded:
            raise RuntimeError("Factory has not been loaded, so no commands are available. Call load() method first!")

        if not self.overlay.command_exists(name):
            log.warning("Command does not exist in %s overlay: %s" % (self._overlay, name))
            return None

        callback = self.overlay.MAPPINGS[name]

        try:
            items = kwargs.pop("items", None)
            if items is not None:
                return ItemizedCommand(callback, items, *args, name=name, **kwargs)

            command = callback(*args, **kwargs)
            command.name = name
            return command
        except (KeyError, NameError, TypeError, ValueError) as e:
            log.critical("Failed to load %s command: %s" % (name, e))
            return None

    def load(self):
        """Load the factory.

        :rtype: bool

        """
        try:
            self.overlay = import_module("scripttease.library.overlays.%s" % self._overlay)
            self.is_loaded = True
        except ImportError as e:
            log.error("The %s overlay could not be imported: %s" % (self._overlay, str(e)))
            pass

        return self.is_loaded
