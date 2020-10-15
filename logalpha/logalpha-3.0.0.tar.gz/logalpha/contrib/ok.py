# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.


"""Simple colorized Ok/Err logging setup."""

# type annotations
from typing import List, IO, Callable

# standard libs
import sys
from dataclasses import dataclass

# internal libs
from ..color import Color, ANSI_RESET
from ..level import Level
from ..message import Message
from ..handler import StreamHandler
from ..logger import Logger


class OkayLogger(Logger):
    """
    Logger with Ok/Err levels.

    Example:
        >>> log = OkayLogger()
        >>> log.ok('foo')

        >>> Logger.handlers.append(OkayHandler())
        >>> log.ok('bar')
        Ok  bar
    """

    levels: List[Level] = Level.from_names(['Ok', 'Err'])
    colors: List[Color] = Color.from_names(['green', 'red'])


# global named levels
OK = OkayLogger.levels[0]  #:
ERR = OkayLogger.levels[1]  #:


@dataclass
class OkayHandler(StreamHandler):
    """
    Writes to <stderr> by default.
    Message format includes the colorized level and the text.

    Attributes:
        level (:class:`~logalpha.level.Level`):
            The level for this handler (default: :data:`OK`).
        resource (`IO`):
            File-like resource to write to (default: :data:`sys.stderr`).
    """

    level: Level = OK
    resource: IO = sys.stderr

    def format(self, message: Message) -> str:
        """Format the message."""
        color = OkayLogger.colors[message.level.value].foreground
        return f'{color}{message.level.name:<3}{ANSI_RESET} {message.content}'
