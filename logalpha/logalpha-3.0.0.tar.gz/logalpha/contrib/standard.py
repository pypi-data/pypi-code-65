# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.


"""Standard logging setup."""

# type annotations
from typing import Type, Callable, IO

# standard libs
import sys
from datetime import datetime
from dataclasses import dataclass
from socket import gethostname

# internal libs
from ..level import Level, WARNING
from ..message import Message
from ..handler import StreamHandler
from ..logger import Logger


@dataclass
class StandardMessage(Message):
    """A message with standard attributes."""
    level: Level
    content: str
    timestamp: datetime
    topic: str
    host: str


@dataclass
class StandardHandler(StreamHandler):
    """
    A standard message handler writes to <stderr> by default.
    Message format includes all attributes.

    Attributes:
        level (:class:`~logalpha.level.Level`):
            The level for this handler.
        resource (:class:`Any`):
            Some resource to publish messages to.
    """

    level: Level = WARNING
    resource: IO = sys.stderr

    def format(self, message: StandardMessage) -> str:
        """Format the message."""
        ts = message.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return f'{ts} {message.host} {message.level.name:<8} [{message.topic}] {message.content}'


# global constant for hostname
HOST: str = gethostname()


class StandardLogger(Logger):
    """Logger with :class:`StandardMessage`."""

    Message: Type[Message] = StandardMessage
    topic: str

    def __init__(self, topic: str) -> None:
        """Initialize with `topic`."""
        super().__init__()
        self.topic = topic
        self.callbacks = {'timestamp': datetime.now,
                          'host': (lambda: HOST),
                          'topic': (lambda: topic)}


DEBUG = Logger.levels[0]  #:
INFO = Logger.levels[1]  #:
WARNING = Logger.levels[2]  #:
ERROR = Logger.levels[3]  #:
CRITICAL = Logger.levels[4]  #:
