""" Module that provides the base class for Fillers, as well as a specialization
    where the Filler is a pie that is filled over time.
"""
from __future__ import annotations

import math

from typing import Tuple, TypeVar

from ._BaseProgress import BaseProgress


_S = TypeVar('S', bound='Filler')


class Filler(BaseProgress):
    """ Base class for creating a Filler.

    Fillers are a way to visualize progression using (typically) a single
    character.

    To get the Filler string, simply get the string representation of an
    instance of this class.

    The Filler is primarily a visualization of two different values:
        1) A current value, or the value that is being tracked. This is a number typically greater than zero, but there is no reason it cannot be negative. However, Fillers can never represent values less than zero.
        2) A maximum value. The current value typically never exceeds this value, but there is no reason it cannot in practice. However, the Filler can never represent progress greater than 100%.

    The filler changes based on the percent the current value is of the maximum
    value.

    NOTE: The Filler will not work for the case where the current value is
    expected to decrement to a minimum value. This case will always have the
    Filler appear to be completely full.

    Fillers can be customized in a variety of ways. For example, the user may
    change what characters are used to show progression. By default, the Filler
    is represented as a single rising vertical bar in 9 steps. These steps are
    called the fill_stages.

    The user may also optionally add a prefix or suffix to the Filler, to be
    displayed to the immediate left or right of the Filler, respectively.

    The prefix and suffix may contain replacement fields that can automatically
    be filled with information relevant to the Filler. There are four predefined
    replacement fields that can be used:
        1) `percent` - Insert the percent (i.e. current_value / max_value) the Filler has been filled.
        2) `current_value` - Insert the current value of the Filler.
        3) `max_value` - Insert the maximum value of the progress bar.
        4) `remaining` - Insert the amount of progress remaining (i.e. max_value - current_value)

    The user can also define any custom replacement fields in either of these
    areas, as well as optionally providing the mapping to evaluate and replace
    them. These mappings are called the prefix_replacement_fields for the prefix
    and suffix_replacement_fields for the suffix.

    Unlike the default behavior of `string.format()`, if the user includes
    replacement fields in any of these strings that do not have values mapped
    for replacement, no error will be thrown. Instead, the replacement fields
    will remain in the string, untouched, so taht the user may replace them at
    a later time.

    Keyword arguments:
        `max_value` -- The maximum value for the number to track before it is considered "complete" (default 100)
        `current_value` -- The current value of the tracked number (default 0)
        `increment_by` -- The amount to increment the current value when next() is called (defualt 1)
        `cap_value` -- Should the tracked number be capped by the max_value, never being allowed to exceed it? (default True)
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by, cap_value)

        self._fill_stages: Tuple[str] = (u' ', u'▁',
                                         u'▂', u'▃', u'▄', u'▅', u'▆', u'▇', u'█')

    def __str__(self):
        prefix = self.formatted_prefix()
        if prefix != '':
            prefix = prefix + ' '
        suffix = self.formatted_suffix()
        if suffix != '':
            suffix = ' ' + suffix

        stage_index = math.floor(
            max(0, min((len(self._fill_stages) - 1) * self.percent(), self._max_value)))

        return prefix + self._fill_stages[stage_index] + suffix

    def get_fill_stages(self) -> Tuple[str]:
        """ Get the tuple that defines the different stages the Filler iterates
            through.
        """
        return self._fill_stages

    def set_fill_stages(self: _S, val: Tuple[str]) -> _S:
        """ Set the different stages the Filler iterates through.

        Keyword arguments:
            `val` - A tuple containing the stages the Filler iterates through.
        """
        self._fill_stages = val
        return self


class Pie(Filler):
    """ Specialization of Filler where the stages are a circle that gets filled
        in by quarters until it is full.
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = False):
        super().__init__(max_value, current_value, increment_by, cap_value)

        self._fill_stages = ('○', '◔', '◑', '◕', '●')
