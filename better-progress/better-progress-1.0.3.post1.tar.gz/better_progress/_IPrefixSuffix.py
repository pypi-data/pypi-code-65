from __future__ import annotations

import abc
import string

from typing import TypeVar


class _EndStringFormatter(string.Formatter):
    """ Custom string formatter to not throw errors when args or kwargs are missing."""

    def get_value(self, key, args, kwargs):
        if isinstance(key, int):
            if len(args) > key:
                return args[key]
            else:
                return '{{}}'
        return kwargs[key] if key in kwargs else '{{{}}}'.format(key)


_S = TypeVar('S', bound='IPrefixSuffix')


class IPrefixSuffix(abc.ABC):
    """ Interface used for everything in this library.

    This interface allows for prefixes and suffixes to be added to a class, and
    to allow the formatting of those prefixes/suffixes without throwing errors
    when an argument is missing from formatting.

    The default prefix and suffix is an empty string.
    The default kwargs for prefix and suffix are empty dicts.

    Usage:
        Assume x is an instance of a class that inherits from IPrefixSuffix.

        # Set a prefix while optionally specifying replacement fields as kwargs
        x.set_prefix('print before everything')
        x.set_prefix('print before with formatting {arg}', arg='my kwarg')
        x.set_prefix('print before with formatting {arg}')

        # Set a suffix while optionally specifying replacement fields as kwargs
        x.set_suffix('print after everything')
        x.set_suffix('print after with formatting {arg}', arg='my kwarg')
        x.set_suffix('print after with formatting {arg}')

        # Set the replacement field values for prefix/suffix
        x.set_prefix_replacement_fields({'arg': 'my kwarg'})
        x.set_suffix_replacement_fields({'arg': 'my kwarg'})

        # Get the prefix/suffix after formatting
        x.formatted_prefix()
        x.formatted_suffix()

        # Get the prefix/suffix before formatting
        x.get_prefix()
        x.get_suffix()

        # Get the current prefix/suffix replacement field mappings
        x.get_prefix_replacement_fields()
        x.get_suffix_replacement_fields()
    """
    _FORMATTER = _EndStringFormatter()

    def __init__(self):
        self._prefix: str = ''
        self._prefix_replacement_fields: dict = {}
        self._suffix: str = ''
        self._suffix_replacement_fields: dict = {}

    def get_prefix(self) -> str:
        """ Get the prefix without formatting."""
        return self._prefix

    def set_prefix(self: _S, val: str, **kwargs) -> _S:
        """ Set the prefix while optionally specifying any replacement fields.

        Keyword arguments:
            val -- The new prefix
        Optional kwargs:
            Any replacement fields in the prefix
        """
        self._prefix = val
        if len(kwargs) > 0:
            self._prefix_replacement_fields = kwargs
        return self

    def get_prefix_replacement_fields(self) -> dict:
        """ Get the replacement field values for the prefix."""
        return self._prefix_replacement_fields

    def set_prefix_replacement_fields(self: _S, val: dict) -> _S:
        """ Set the replacement field values for the prefix.

        Keyword arguments:
            val -- Dict mapping of replaecment field names to their values
        """
        self._prefix_replacement_fields = val
        return self

    def get_suffix(self) -> str:
        """ Get the suffix without any formatting."""
        return self._suffix

    def set_suffix(self: _S, val: str, **kwargs) -> _S:
        """ Set the suffix while optionally specifying any replacement fields.

        Keyword arugments:
            val -- The new suffix
        Optional kwargs:
            Any replacement fields in the suffix
        """
        self._suffix = val
        if len(kwargs) > 0:
            self._suffix_replacement_fields = kwargs
        return self

    def get_suffix_replacement_fields(self) -> dict:
        """ Get the replacement field values for the suffix."""
        return self._suffix_replacement_fields

    def set_suffix_replacement_fields(self: _S, val: dict) -> _S:
        """ Set the replacement field values for the prefix.

        Keyword arguments:
            val -- Dict mapping of replacement field names to their values
        """
        self._suffix_replacement_fields = val
        return self

    def formatted_prefix(self) -> str:
        """ Get the prefix after formatting using the prefix replacement field mapping."""
        return self._custom_format(self._prefix, self._prefix_replacement_fields)

    def formatted_suffix(self) -> str:
        """ Get the suffix after formatting using the suffix replacement field mapping."""
        return self._custom_format(self._suffix, self._suffix_replacement_fields)

    def _custom_format(self, text: str, relevant_kwargs: dict = {}) -> str:
        """ Format a string with the values in a dict.

        The formatter does not throw errors, even if a replacement field exists
        in the string that does not have a corresponding positional arg or kwarg
        to replace it.

        When one of these replacement fields is found, it is
        ignored and left in the string as-is.
        """
        return IPrefixSuffix._FORMATTER.format(text, **relevant_kwargs)
