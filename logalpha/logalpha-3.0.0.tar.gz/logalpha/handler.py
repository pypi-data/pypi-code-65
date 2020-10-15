# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""Handler implementations."""

# type annotations
from __future__ import annotations
from typing import Any, IO

# standard libs
import sys
from dataclasses import dataclass


# internal libs
from .level import Level, WARNING
from .message import Message


@dataclass
class Handler:
    """
    Core message handling interface.
    A Handler associates a `level` with a `resource`.

    Attributes:
        level (:class:`~logalpha.level.Level`):
            The level for this handler.
        resource (:class:`Any`):
            Some resource to publish messages to.
    """

    level: Level
    resource: Any

    def write(self, message: Message) -> None:
        """Publish `message` to `resource` after calling `format`."""
        raise NotImplementedError()

    def format(self, message: Message) -> Any:
        """Format `message`."""
        raise NotImplementedError()


@dataclass
class StreamHandler(Handler):
    """
    Publish messages to a file-like resource.

    Attributes:
        level (:class:`~logalpha.level.Level`):
            The level for this handler (default: :data:`WARNING`).
        resource (`IO`):
            File-like resource to write to (default: :data:`sys.stderr`).
    """

    level: Level = WARNING
    resource: IO = sys.stderr

    def write(self, message: Message) -> None:
        """Publish `message` to `resource` after calling `format`."""
        print(self.format(message), file=self.resource, flush=True)

    def format(self, message: Message) -> str:
        """Returns :data:`message.content`."""
        return message.content
