""" Module that provides the base class for progress bars, as well as a handfull
    of more customized progress bar types.

    Bar is the base class for all progress bars, and will be the one used most
    often.

    IncrementalBar is a child of Bar, and offers the ability for each tick in
    the progress bar to go through stages as it is filling up.

    The rest of the classes defined in this module are small customizations
    built upon the previous two classes, that are made available as a
    convenience to the user. These classes only change the characters used in
    the progress bar.
"""
from __future__ import annotations

import sys
import math

from typing import TypeVar, List

from ._BaseProgress import BaseProgress


_B = TypeVar('B', bound='Bar')


class Bar(BaseProgress):
    """ Base class for creating a progress bar.

    The Bar class is used to visualize some form of progress using a progress
    bar, given as a string.

    To get the progress bar string, simply get the string representation of an
    instance of this class.

    The progress bar is primarily a visualization of two different values:
        1) A current value, or the value that is being tracked. This is a number typically greater than zero, but there is no reason it cannot be negative. However, negative numbers cannot be represented in the progress bar.
        2) A maximum value. The current value typically never exceeds this value, but there is no reason it cannot in practice. However, the progress bar can never represent progress greater than 100%.

    The progress bar will be filled based on the percent the current value is
    of the maximum value.

    NOTE: The progress bar will not work for the case where the current value
    is expected to decrement to a minimum value. This case will always have the
    progress bar appear to be completely full.

    The progress bar can be customized in a variety of ways. For example,
    the user may change what character (or characters) are used to show
    progression in the bar. By default, the filled part of the bar is
    represented with a '#' character, and the empty part of the bar is
    represented with a space, or ' ' character. These two characters are called
    the fill_character and the empty_character, respectively.

    The two ends of the bar, denoting where the actual bar begins and ends, can
    also be customized. By default, both are represented using the '|'
    character, but can be changed to any character, or characters. Each end can
    also be represented with different characters than the other. These two
    characters are called the bar_prefix and bar_suffix, for the beginning and
    end respectively.

    The user may also optionally add a prefix or suffix to the bar, to be
    displayed before the bar_prefix or after the bar_suffix. This is meant to
    hold any extra info the programmer may want to convey. These are called the
    prefix and suffix.

    The prefix, bar_prefix, bar_suffix, and suffix may contain replacement
    fields that can automatically be filled with information relevant to the
    progress bar. There are four predefined replacement fields that can be used:
        1) `percent` - Insert the percent (i.e. current_value / max_value) the progress bar has been filled.
        2) `current_value` - Insert the current value of the progress bar.
        3) `max_value` - Insert the maximum value of the progress bar.
        4) `remaining` - Insert the amount of progress remaining (i.e. max_value - current_value)

    The user can also define any custom replacement fields in any of these
    areas, as well as optionally providing the mapping to evaluate and replace
    them. These mappings are called the prefix_replacement_fields for the
    prefix, bar_prefix_replacement_fields for the bar_prefix,
    bar_suffix_replacement_fields for the bar_suffix, and the
    suffix_replacement_fields for the suffix.

    Unlike the default behavior of `string.format()`, if the user includes
    replacement fields in any of these strings that do not have values mapped
    for replacement, no error will be thrown. Instead, the replacement fields
    will remain in the string, untouched, so that the user may replace them at
    a later time.

    Keyword arguments:
        `max_value` -- The maximum value for the number to track before it is considered "complete" (default 100)
        `current_value` -- The current value of the tracked number (default 0)
        `increment_by` -- The amount to increment the current value when next() is called (defualt 1)
        `cap_value` -- Should the tracked number be capped by the max_value, never being allowed to exceed it? (default True)
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by)

        self._bar_width: int = 32
        self._fill_character: str = '#'
        self._empty_character: str = ' '
        self._bar_prefix: str = '|'
        self._bar_prefix_replacement_fields: dict = {}
        self._bar_suffix: str = '|'
        self._bar_suffix_replacement_fields: dict = {}

    def __str__(self):
        filled = math.floor(self._bar_width * self.percent())
        empty = self._bar_width - filled
        prefix = self.formatted_prefix()
        if prefix != '':
            prefix = prefix + ' '
        suffix = self.formatted_suffix()
        if suffix != '':
            suffix = ' ' + suffix
        bar_prefix = self.formatted_bar_prefix()
        bar_suffix = self.formatted_bar_suffix()

        return prefix + bar_prefix + (self._fill_character * filled) + (self._empty_character * empty) + bar_suffix + suffix

    def get_bar_width(self) -> int:
        """ Get the number of ticks used in the progress bar."""
        return self._bar_width

    def set_bar_width(self: _B, val: int) -> _B:
        """ Change the number of ticks used in the progress bar.

        Keyword arguments:
            `val` -- The number of ticks to use.
        """
        self._bar_width = val
        return self

    def get_fill_character(self) -> str:
        """ Get the character(s) used to represent the filled portion of the
            progress bar.
        """
        return self._fill_character

    def set_fill_character(self: _B, val: str) -> _B:
        """ Set the character(s) used to represent the filled portion of the
            progress bar.

            Keyword arguments:
                `val` -- The character(s) to be used to represent the filled portion of the progress bar.
        """
        self._fill_character = val
        return self

    def get_empty_character(self) -> str:
        """ Get the character(s) used to represent the empty portion of the
            progress bar.
        """
        return self._empty_character

    def set_empty_character(self: _B, val: str) -> _B:
        """ Set the character(s) used to represent the empty portion of the
            progress bar.

            Keyword arguments:
                `val` -- The character(s) to be used to represent the empty portion of the progress bar.
        """
        self._empty_character = val
        return self

    def get_bar_prefix(self) -> str:
        """ Get the character(s) used to represent the left border of the
            progress bar without any formatting.
        """
        return self._bar_prefix

    def set_bar_prefix(self: _B, val: str) -> _B:
        """ Set the character(s) used to represent the left border of the
            progress bar.

            Keyword arguments:
                `val` -- The character(s) to be used to represent the left border of the progress bar.
        """
        self._bar_prefix = val
        return self

    def get_bar_prefix_replacement_fields(self) -> dict:
        """ Get the replacement field values for the bar_prefix."""
        return self._bar_prefix_replacement_fields

    def set_bar_prefix_replacement_fields(self: _B, val: dict) -> _B:
        """ Set the replacement field values for the bar_prefix.

        Keyword arguments:
            `val` -- Dict mapping of replacement field names to their values.
        """
        self._bar_prefix_replacement_fields = val
        return self

    def get_bar_suffix(self) -> str:
        """ Get the character(s) used to represent the right border of the
            progress bar without any formatting.
        """
        return self._bar_suffix

    def set_bar_suffix(self: _B, val: str) -> _B:
        """ Set the character(s) used to represent the right border of the
            progress bar.

            Keyword arguments:
                `val` -- The character(s) to be used to represent the right border of the progress bar.
        """
        self._bar_suffix = val
        return self

    def get_bar_suffix_replacement_fields(self) -> dict:
        """ Get the replacement field values for the bar_suffix."""
        return self._bar_suffix_replacement_fields

    def set_bar_suffix_replacement_fields(self: _B, val: dict) -> _B:
        """ Set the replacement field values for the bar_suffix.

        Keyword arguments:
            `val` -- Dict mapping of replacement field names to their values.
        """
        self._bar_suffix_replacement_fields = val
        return self

    def formatted_bar_prefix(self) -> str:
        """ Get the bar_prefix after formatting with any defined replacement
            field values.
        """
        return self._custom_format(self._bar_prefix, self._bar_prefix_replacement_fields)

    def formatted_bar_suffix(self) -> str:
        """ Get the bar_suffix after formatting with any defined replacement
            field values.
        """
        return self._custom_format(self._bar_suffix, self._bar_suffix_replacement_fields)


_I = TypeVar('I', bound='IncrementalBar')


class IncrementalBar(Bar):
    """ Progress bar that lets you define different stages for each Bar tick.

    For example, let's say a single tick represents 10% of the total progress
    bar. By default, an IncrementalBar has two different stages for a single
    tick (on Windows, other platforms have more). The first stage is ' ', or
    empty. The second stage is '▌', or a half-filled bar character. At 0-4%, the
    first tick will be the ' ' character. At 5-9%, the first tick will change to
    the half-filled bar character. At 10%, the first tick will change to '█',
    which is the default fill_character, and the second tick will become the ' '
    character.

    Each fill stage represents a percentage complete proportional to the total
    size of the progress bar.

    Keyword arguments:
        `max_value` -- The maximum value for the number to track before it is considered "complete" (default 100)
        `current_value` -- The current value of the tracked number (default 0)
        `increment_by` -- The amount to increment the current value when next() is called (defualt 1)
        `cap_value` -- Should the tracked number be capped by the max_value, never being allowed to exceed it? (default True)
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by, cap_value)

        if sys.platform.startswith('win'):
            self._fill_stages: List[str] = [u' ', u'▌']
        else:
            self._fill_stages: List[str] = [
                u' ', u'▏', u'▎', u'▍', u'▌', u'▋', u'▊', u'▉']

        self._fill_character = '█'

    def __str__(self):
        filled = self._bar_width * self.percent()
        has_partial = math.modf(filled)[0] != 0
        full_filled = math.floor(filled)
        stage_index = math.floor(math.modf(filled)[0] * len(self._fill_stages))
        empty = self._bar_width - full_filled - (1 if has_partial else 0)

        bar_prefix = self.formatted_bar_prefix()
        bar_suffix = self.formatted_bar_suffix()

        prefix = self.formatted_prefix()
        if prefix != '':
            prefix = prefix + ' '
        suffix = self.formatted_suffix()
        if suffix != '':
            suffix = ' ' + suffix

        return prefix + bar_prefix + (self._fill_character * full_filled) + (self._fill_stages[stage_index] if has_partial else '') + (self._empty_character * empty) + bar_suffix + suffix

    def get_fill_stages(self) -> List[str]:
        """ Get the stages each tick in the progress bar goes through."""
        return self._fill_stages

    def set_fill_stages(self: _I, stages: List[str]) -> _I:
        """ Set the stages each tick in the progress bar goes through.

        Keyword arguments:
            `stages` -- List of the stages each tick in the progress bar goes through.
        """
        self._fill_stages = stages
        return self


class RaisingIncrementalBar(IncrementalBar):
    """ Specialization of IncrementalBar where the ticks are bars that rise 
        vertically.
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by, cap_value)

        self._fill_stages = [
            u' ', u'▁', u'▂', u'▃', u'▄', u'▅', u'▆', u'▇']
        self._fill_character = '█'


class PixelBar(IncrementalBar):
    """ Specialization of IncrementalBar where the ticks are 1-8 pixels in a
        2x4 rectangle.
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by, cap_value)

        self._fill_stages = [' ', '⡀', '⡄', '⡆', '⡇', '⣇', '⣧', '⣷']
        self._fill_character = '⣿'


class ShadyBar(IncrementalBar):
    """ Specialization of IncrementalBar where the ticks are rectangles that
        increase in opacity.
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by, cap_value)

        self._fill_stages = [' ', '░', '▒', '▓']
        self._fill_character = '█'


class ChargingBar(Bar):
    """ Specialization of Bar where the fill character is a rectangle, the empty
        character is a '.', and the bar prefix/suffix are empty.
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by, cap_value)

        self._fill_character = '█'
        self._empty_character = '.'
        self._bar_prefix = ''
        self._bar_suffix = ''


class FillingSquaresBar(ChargingBar):
    """ Specialization of ChargingBar where the fill and empty characters are
        squares.
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by, cap_value)

        self._empty_character = '▢'
        self._fill_character = '▣'


class FillingCirclesBar(ChargingBar):
    """ Specialization of ChargingBar where the fill and empty characters are
        circles.
    """

    def __init__(self, max_value: float = 100, current_value: float = 0, increment_by: float = 1, cap_value: bool = True):
        super().__init__(max_value, current_value, increment_by, cap_value)

        self._empty_character = '◯'
        self._fill_character = '◉'
