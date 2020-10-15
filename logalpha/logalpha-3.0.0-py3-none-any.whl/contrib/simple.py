# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.


"""Simple logging setup with colors."""

# type annotations
from typing import Type, Callable, IO

# standard libs
import sys
from dataclasses import dataclass

# internal libs
from ..color import ANSI_RESET
from ..level import CRITICAL, Level, WARNING
from ..message import Message
from ..handler import StreamHandler
from ..logger import Logger


@dataclass
class SimpleMessage(Message):
    """A message with a named `topic`."""
    level: Level
    content: str
    topic: str


class SimpleLogger(Logger):
    """Logger with :class:`SimpleMessage`."""

    Message: Type[Message] = SimpleMessage
    topic: str

    def __init__(self, topic: str) -> None:
        """Initialize with `topic`."""
        super().__init__()
        self.topic = topic
        self.callbacks = {'topic': (lambda: topic)}


@dataclass
class SimpleHandler(StreamHandler):
    """
    Writes to <stderr> by default.
    Message format includes topic and level name.

    Attributes:
        level (:class:`~logalpha.level.Level`):
            The level for this handler.
        resource (:class:`Any`):
            Some resource to publish messages to.
    """

    level: Level = WARNING
    resource: IO = sys.stderr

    def format(self, message: SimpleMessage) -> str:
        """Format the message."""
        return f'{message.level.name:<8} [{message.topic}] {message.content}'


@dataclass
class ColorHandler(StreamHandler):
    """
    Writes to <stderr> by default.
    Message format colorizes level name.

    Attributes:
        level (:class:`~logalpha.level.Level`):
            The level for this handler.
        resource (:class:`Any`):
            Some resource to publish messages to.
    """

    level: Level = WARNING
    resource: IO = sys.stderr

    def format(self, message: SimpleMessage) -> str:
        """Format the message."""
        color = SimpleLogger.colors[message.level.value].foreground
        return f'{color}{message.level.name:<8}{ANSI_RESET} [{message.topic}] {message.content}'


DEBUG = Logger.levels[0]  #:
INFO = Logger.levels[1]  #:
WARNING = Logger.levels[2]  #:
ERROR = Logger.levels[3]  #:
CRITICAL = Logger.levels[4]  #:
