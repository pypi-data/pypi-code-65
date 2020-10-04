from typing import *

from .message_handler import *

class CommandHandler(OnMentionHandler):
    command: Union[str, Collection[str]]
    num_args: Optional[int] = None
    
    async def can_handle(self, event: MessageEvent) -> bool:
        return await super().can_handle(event) \
           and await self._can_handle__check_command(event)
    
    async def _can_handle__check_command(self, event: MessageEvent) -> bool:
        cmd, params = await self.parse_command(event)
        
        return (isinstance(self.command.lower(), str) and cmd == self.command or not isinstance(cmd, str) and cmd in self.command) \
            and (self.num_args is None or len(params) == self.num_args)
    
    async def parse_command(self, event: MessageEvent) -> Tuple[str, List[str]]:
        words = event.message.text.split()
        return words[1].lower(), words[2:]
    
    async def handle_event(self, event: MessageEvent):
        cmd, params = await self.parse_command(event)
        return await self.handle_command(event, cmd, *params)
    
    async def handle_command(self, event: MessageEvent, command: str, *params: str):
        pass


__all__ = \
[
    'CommandHandler',
]
