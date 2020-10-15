# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""ANSI color definitions."""

# type annotations
from __future__ import annotations
from typing import List, Dict

# standard libs
from dataclasses import dataclass, field


#: Names of supported colors to map to ANSI codes.
NAMES: List = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

#: ANSI reset code.
ANSI_RESET: str = '\033[0m'

#: Dictionary of all ANSI code sequences.
ANSI_COLORS: Dict[str, Dict[str, str]] = {
    prefix: {color: '\033[{prefix}{num}m'.format(prefix=i + 3, num=j) for j, color in enumerate(NAMES)}
    for i, prefix in enumerate(['foreground', 'background'])
}


@dataclass
class Color:
    """
    Associates a name (str) with its corresponding foreground and background (str)
    ANSI codes. Construct one or more instances using the factory methods.
    """

    name: str
    foreground: str
    background: str

    # the ANSI reset code is an attribute but not a variable
    reset: str = field(default=ANSI_RESET, init=False, repr=False)

    @classmethod
    def from_name(cls, name: str) -> Color:
        """
        Lookup ANSI codes by `name`.

        Example:
            >>> red = Color.from_name('red')
            >>> red
            Color(name='red', foreground='[31m', background='[41m')
        """
        return cls(name, ANSI_COLORS['foreground'][name], ANSI_COLORS['background'][name])

    @classmethod
    def from_names(cls, names: List[str]) -> List[Color]:
        """
        Returns a tuple of Color instances using the singular :meth:`from_name` factory.

        Example:
            >>> colors = Color.from_names(['blue', 'green'])
            >>> colors
            [Color(name='blue', foreground='[34m', background='[44m'),
             Color(name='green', foreground='[32m', background='[42m')]
        """
        return [cls.from_name(name) for name in names]


# global named instances of colors
COLORS  = Color.from_names(NAMES)  #:
BLACK   = COLORS[0]  #:
RED     = COLORS[1]  #:
GREEN   = COLORS[2]  #:
YELLOW  = COLORS[3]  #:
BLUE    = COLORS[4]  #:
MAGENTA = COLORS[5]  #:
CYAN    = COLORS[6]  #:
WHITE   = COLORS[7]  #:
