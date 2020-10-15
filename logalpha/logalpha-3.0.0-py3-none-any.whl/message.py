# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""Base Message type."""

# type annotations
from __future__ import annotations
from typing import Any

# standard libs
from dataclasses import dataclass

# internal libs
from .level import Level, INFO


@dataclass
class Message:
    """
    Associates a level with content. Derived classes should add new fields.
    The :class:`~logalpha.logger.Logger` should define `callbacks` to populate
    these new fields.

    Example:
        >>> msg = Message(level=INFO, content='Hello, world!')
        Message(level=Level(name='INFO', value=1), content='Hello, world!')

    See Also:
        :class:`logalpha.logger.Logger`

    .. note::

        It is not intended that you directly instantiate a message. Messages
        are automatically constructed by the :class:`~logalpha.logger.Logger`
        when calling one of the instrumented level methods.
    """
    level: Level
    content: Any
