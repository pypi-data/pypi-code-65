from abc import ABC
from functools import partial
from typing import *

from dataclasses import dataclass

from ..bot_api import User
from ..errors import BotError
from ...util import Logging

@dataclass(frozen=True)
class Event:
    bot_user: User
    base_error: Type[Exception]

class EventHandler(Logging, ABC):
    async def can_handle(self, event: Event) -> bool:
        return await self._can_handle__check_event_type(event)
    
    async def _can_handle__check_event_type(self, event: Event) -> bool:
        return isinstance(event, Event)
    
    async def handle_if_can(self, event: Event) -> bool:
        if (await self.can_handle(event)):
            await self._safe_handle_event(event)
            return True
        else:
            return False
    
    async def _safe_handle_event(self, event: Event):
        try:
            return await self.handle_event(event)
        except Exception as e:
            return await self.handle_error(event, e)
    
    async def handle_event(self, event: Event):
        pass
    
    async def handle_error(self, event: Event, error: Exception):
        prefix = "Got unhandled error"
        if (isinstance(error, BotError)):
            func = self.logger.error
        elif (isinstance(error, NotImplementedError)):
            func = partial(self.logger.warning, exc_info=True)
            prefix = "Unhandled non-implemented call detected"
        else:
            func = self.logger.exception
        
        func(f"{prefix}: {type(error).__name__}: '{error}'")

__all__ = \
[
    'Event',
    'EventHandler',
]
