""" Module that provides the base class for Spinners, as well as a handfull of
    specializations.
"""
from __future__ import annotations

from typing import Tuple, TypeVar

from ._IPrefixSuffix import IPrefixSuffix


_S = TypeVar('S', bound='Spinner')


class Spinner(IPrefixSuffix):
    """ Base class for creating a Spinner.

    Spinners are a way to convey that work is being done through a looping
    sequence of characters.

    To get the Spinner string, simply get the string representation of an
    instance of this class.

    By default, the Spinner iterates through the character sequence '-', '\\\\',
    '|', and '/', before it loops back to the beginning.

    The user can specify a custom sequence by calling `set_stages(stage_tuple)`,
    and providing the stages in the function parameter.

    To change the stage the Spinner is on, either call
    `set_current_stage(stage_index)` or `next()`.

    Spinners can be given a prefix or suffix, which will be displayed to the
    immediate left or right of the Spinner, respectively.

    The prefix and suffix may contain replacement fields that can automatically
    be filled with information relevant to the Spinner. There are four
    predefined replacement fields that can be used:
        1) `percent` - Insert the percent (i.e. current_value / max_value) the Spinner has been filled.
        2) `current_value` - Insert the current value of the Spinner.
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
    """

    def __init__(self):
        super().__init__()

        self._stages: Tuple[str] = ('-', '\\', '|', '/')
        self._current_stage: int = 0

    def __str__(self):
        prefix = self.formatted_prefix()
        if prefix != '':
            prefix = prefix + ' '
        suffix = self.formatted_suffix()
        if suffix != '':
            suffix = ' ' + suffix

        return prefix + self._stages[self._current_stage] + suffix

    def get_stages(self) -> Tuple[str]:
        """ Get the stages the Spinner iterates through."""
        return self._stages

    def set_stages(self: _S, val: Tuple[str]) -> _S:
        """ Set the different stages the Spinner iterates through.

        Keyword arguments:
            `val` - A tuple containing the stages the Spinner iterates through.
        """
        self._stages = val
        return self

    def get_current_stage(self) -> int:
        """ Get the index of the current stage the Spinner is on."""
        return self._current_stage

    def set_current_stage(self: _S, val: int) -> _S:
        """ Set the index of the stage the Spinner should be on.

        Keyword arguments:
            `val` - Index of the stage the Spinner should be on.
        """
        self._current_stage = val
        return self

    def next(self):
        """ Iterate the Spinner to its next stage."""
        self._current_stage = (self._current_stage + 1) % len(self._stages)


class PieSpinner(Spinner):
    """ Specialization of Spinner where the stages are a circle with a quarter
        outlined.
    """

    def __init__(self):
        super().__init__()

        self._stages = ('◷', '◶', '◵', '◴')


class MoonSpinner(Spinner):
    """ Specialization of Spinner where the stages are a circle with half filled
        in.
    """

    def __init__(self):
        super().__init__()

        self._stages = ('◑', '◒', '◐', '◓')


class LineSpinner(Spinner):
    """ Specialization of Spinner where the stages are a line that move up and
        down.
    """

    def __init__(self):
        super().__init__()

        self._stages = ('⎺', '⎻', '⎼', '⎽', '⎼', '⎻')


class PixelSpinner(Spinner):
    """ Specialization of Spinner where the stages are a 2x4 rectangle of pixels
        where a single missing pixel rotates clockwise.
    """

    def __init__(self):
        super().__init__()

        self._stages = ('⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽')
