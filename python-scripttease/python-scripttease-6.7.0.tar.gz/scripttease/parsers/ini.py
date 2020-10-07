# Imports

from commonkit import parse_jinja_template, read_file, smart_cast, split_csv
from configparser import ConfigParser, ParsingError
import logging
import os
from ..constants import LOGGER_NAME
from ..library.commands import ItemizedCommand
from ..library.commands.templates import Template
from .base import Parser

log = logging.getLogger(LOGGER_NAME)

# Exports

__all__ = (
    "Config",
)

# Classes


class Config(Parser):
    """An INI configuration for loading commands."""

    def load(self):
        """Load commands from a INI file."""
        if not self.exists:
            return False

        if not self.factory.load():
            return False

        ini = self._load_ini()
        if ini is None:
            return False

        success = True
        for comment in ini.sections():
            args = list()
            command_name = None
            count = 0
            kwargs = self.options.copy()
            kwargs['comment'] = comment

            for key, value in ini.items(comment):
                # The first key/value pair is the command name and arguments.
                if count == 0:
                    command_name = key

                    # Arguments surrounded by quotes are considered to be one argument. All others are split into a
                    # list to be passed to the callback.
                    if value[0] == '"':
                        args.append(value.replace('"', ""))
                    else:
                        args = value.split(" ")
                else:
                    _key, _value = self._get_key_value(key, value)

                    kwargs[_key] = _value

                count += 1

            command = self.factory.get_command(command_name, *args, **kwargs)
            if command is not None:
                if isinstance(command, self.factory.overlay.Function):
                    self._functions.append(command)
                elif isinstance(command, Template):
                    self._load_template(command)
                    self._commands.append(command)
                elif isinstance(command, ItemizedCommand):
                    itemized_template = False
                    for c in command.get_commands():
                        if isinstance(c, Template):
                            itemized_template = True
                            self._load_template(c)
                            self._commands.append(c)

                    if not itemized_template:
                        self._commands.append(command)
                else:
                    self._commands.append(command)

                # if isinstance(command, Function):
                #     self._functions.append(command)
                # elif isinstance(command, Include):
                #     subcommands = self._load_include(command)
                #     if subcommands is not None:
                #         self._commands += subcommands
                # elif isinstance(command, Template):
                #     self._load_template(command)
                #     self._commands.append(command)
                # elif isinstance(command, ItemizedCommand) and issubclass(command.command_class, Template):
                #     for c in command.get_commands():
                #         self._load_template(c)
                #         self._commands.append(c)
                # else:
                #     self._commands.append(command)
            else:
                success = False

        self.is_loaded = success
        return self.is_loaded

    # noinspection PyMethodMayBeStatic
    def _get_key_value(self, key, value):
        """Process a key/value pair from an INI section.

        :param key: The key to be processed.
        :type key: str

        :param value: The value to be processed.

        :rtype: tuple
        :returns: The key and value, both of which may be modified from the originals.

        """
        if key in ("environments", "environs", "envs", "env"):
            _key = "environments"
            _value = split_csv(value)
        elif key in ("func", "function"):
            _key = "function"
            _value = value
        elif key == "items":
            _key = "items"
            _value = split_csv(value)
        elif key == "tags":
            _key = "tags"
            _value = split_csv(value)
        else:
            _key = key
            _value = smart_cast(value)

        return _key, _value

    def _load_ini(self):
        """Load the configuration file.

        :rtype: ConfigParser | None

        """
        ini = ConfigParser()
        if self.context is not None:
            try:
                content = parse_jinja_template(self.path, self.context)
            except Exception as e:
                log.error("Failed to parse %s as template: %s" % (self.path, e))
                return None
        else:
            content = read_file(self.path)

        try:
            ini.read_string(content)
            return ini
        except ParsingError as e:
            log.error("Failed to parse %s: %s" % (self.path, e))
            return None

    def _load_template(self, command):
        """Load additional resources for a template command.

        :param command: The template command.
        :type command: Template

        """
        # This may produce problems if template kwargs are the same as the given context.
        if self.context is not None:
            command.context.update(self.context)

        # Custom locations come before default locations.
        command.locations += self.locations

        # This allows template files to be specified relative to the configuration file.
        command.locations.append(os.path.join(self.directory, "templates"))
        command.locations.append(self.directory)
