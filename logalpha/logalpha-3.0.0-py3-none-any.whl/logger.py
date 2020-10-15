# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.


"""Logger implementations."""

# type annotations
from __future__ import annotations
from typing import List, Dict, Callable, Any, Type

# standard libs
import functools

# internal libs
from .level import Level, DEBUG, INFO, WARNING, ERROR, CRITICAL
from .color import Color, BLUE, GREEN, YELLOW, RED, MAGENTA
from .handler import Handler, StreamHandler
from .message import Message


# dictionary of parameter-less functions
CallbackMethod = Callable[[], Any]


class Logger:
    """
    Base logging interface.

    By default the `levels` and `colors` are the conventional set.
    Append any number of appropriate handlers.

    Example:
        >>> log = Logger()
        >>> log.warning('foo')

        >>> Logger.handlers.append(StreamHandler())
        >>> log.warning('bar')
        bar
    """

    # default configuration
    levels: List[Level] = [DEBUG, INFO, WARNING, ERROR, CRITICAL]
    colors: List[Color] = [BLUE, GREEN, YELLOW, RED, MAGENTA]
    handlers: List[Handler] = []

    callbacks: Dict[str, CallbackMethod] = dict()

    # redefine to construct with callbacks
    Message: Type[Message] = Message

    def write(self, level: Level, content: Any) -> None:
        """
        Publish `message` to all `handlers` if its `level` is sufficient for that handler.

        .. note::

            It's expected that the logger will be called with one of the dynamically
            instrumented level methods (e.g., :meth:`info`), and not call the
            :meth:`write` method directly.
        """
        message = self.Message(level=level, content=content, **self._evaluate_callbacks())  # noqa: args
        for handler in self.handlers:
            if message.level >= handler.level:
                handler.write(message)

    def _evaluate_callbacks(self) -> Dict[str, Any]:
        """Evaluates all methods in `callbacks` dictionary."""
        return dict(zip(self.callbacks.keys(), map(lambda method: method(), self.callbacks.values())))

    @property
    @functools.lru_cache(maxsize=None)
    def _level_map(self) -> Dict[str, Level]:
        """Map lower-case level names to level instances."""
        return {level.name.lower(): level for level in self.levels}

    @functools.lru_cache(maxsize=None)
    def __getattr__(self, name: str) -> Any:
        """Automatically forward calls to level `name`."""
        try:
            return functools.partial(self.write, self._level_map[name])
        except KeyError as error:
            raise AttributeError(f'\'{self.__class__.__name__}\' object has no attribute \'{name}\'') from error
