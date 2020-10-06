from __future__ import annotations

import abc
import string

from typing import TypeVar

from ._IPrefixSuffix import IPrefixSuffix


_S = TypeVar('S', bound='BaseProgress')


class BaseProgress(IPrefixSuffix):
    """ Base class for things that can progress toward a max value.

    NOTE: This class contains an abstract method, and should therefore never be
    used by itself.

    This class facilitates keeping track of a number's current value toward
    some maximum, and incrementing the number by some constant.

    Keyword arguments:
        max_value -- The maximum value for the number to track before it is considered "complete" (default 100)
        current_value -- The current value of the tracked number (defualt 0)
        increment_by -- The amount to increment the current value when next() is called (default 1)
        cap_value -- Should the tracked number be capped by the max_value, never being allowed to exceed it? (default True)
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__()

        self._max_value = max_value
        self._current_value = current_value
        self._increment_by = increment_by
        self._cap_value = cap_value

    @abc.abstractmethod
    def __str__(self):
        """ Abstract string conversion.

        Get a pretty, human-readable output of the current value.
        """
        return '{} / {}'.format(self._current_value, self._max_value)

    def get_max_value(self) -> float:
        """ Get the currently set maximum value."""
        return self._max_value

    def set_max_value(self: _S, val: float) -> _S:
        """ Change the maximum value for the tracked number.

        If the maximum value is set below the current value, and the value is
        capped, the current value will automatically lower to the new max value.

        Keyword arguments:
            val -- the new maximum value
        """
        self._max_value = val
        # Cap the current value if necessary
        self.set_current_value(self.get_current_value())
        return self

    def get_current_value(self) -> float:
        """ Get the currently set current value."""
        return self._current_value

    def set_current_value(self: _S, val: float) -> _S:
        """ Change the current value of the tracked number.

        If the current value is set above the maximum value,a nd the value is
        capped, the current value will be set to the maximum value.

        Keyword arguments:
            val -- the new current value
        """
        if self._cap_value:
            self._current_value = min(self._max_value, val)
        else:
            self._current_value = val
        return self

    def get_increment_by(self) -> float:
        """ Get the value calling next() increments the current value by."""
        return self._increment_by

    def set_increment_by(self: _S, val: float) -> _S:
        """ Change the value calling next() increments the current value by.

        Keyword arguments:
            val -- the new amount to increment the current value by when next() is called.
        """
        self._increment_by = val
        return self

    def get_cap_value(self) -> bool:
        """ Should the current value be capped at the max value?"""
        return self._cap_value

    def set_cap_value(self: _S, cap: bool) -> _S:
        """ Set if the tracked value should be capped at the max value.

        If this is set, the tracked value will never exceed the max value. If
        the current value exceeds the max value when this is set, the current
        value will be lowered to the max value. If the current value is set to
        a number greater than the max value and this is set, it will
        automatically be lowered to the max value.

        Keyword arguments:
            val -- Should the tracked value be capped at the max value?
        """
        self._cap_value = cap
        # Cap the current value if necessary
        self.set_current_value(self.get_current_value())
        return self

    def percent(self) -> float:
        """
        Get the percent the current value is toward the max value.

        This is returned as a percentage from 0-1, unless the current value is
        negative or exceeds the max value. In these cases, the value will be
        negative or greater than 1, respectively.
        """
        return self._current_value / self._max_value

    def remaining(self) -> float:
        """ Get the difference between the max value and the current value."""
        return self._max_value - self._current_value

    def complete(self) -> bool:
        """ Has the current value reached the max value?"""
        return self._current_value >= self._max_value

    def next(self):
        """ Incremenet the current value by the amount set by increment_by."""
        self._current_value += self._increment_by
        if self._cap_value and self._current_value > self._max_value:
            self._current_value = self._max_value

    def _custom_format(self, text: str, relevant_kwargs: dict = {}) -> str:
        """ Function for formatting the prefix, bar_prefix, suffix, and bar_suffix."""
        kwargs = {
            **relevant_kwargs,
            'percent': self.percent() * 100,
            'current_value': self.get_current_value(),
            'max_value': self.get_max_value(),
            'remaining': self.remaining()
        }
        return super()._custom_format(text, kwargs)
