from typing import *

import discord
from dataclasses import replace

from botter import BotBase
from ..api.bot_api import *
from ..util.os_operations import safe_remove

class DiscordUser(User):
    discord_user: discord.user.BaseUser
    client: discord.Client
    
    def __init__(self, client: discord.Client, user: discord.user.BaseUser):
        self.discord_user = user
        self.client = client
        
        super().__init__ \
        (
            id = str(self.discord_user.id),
            user_name = self.discord_user.name,
            display_name = self.discord_user.display_name,
        )

SUPPORTED_AUDIO_FORMATS = { 'mp3' }
class DiscordAttachment(Attachment):
    discord_attachment: discord.Attachment
    client: discord.Client
    
    def __init__(self, client: discord.Client, attachment: discord.Attachment):
        self.discord_attachment = attachment
        self.client = client
        
        super().__init__ \
        (
            id = str(self.discord_attachment.id),
            filename = self.discord_attachment.filename,
            type = AttachmentType.Image if (self.is_image) else AttachmentType.Audio if (self.is_audio) else AttachmentType.Document,
        )
    
    @property
    def is_image(self) -> bool:
        return self.discord_attachment.height is not None
    @property
    def is_audio(self) -> bool:
        return self.discord_attachment.filename.lower().rpartition('.')[-1] in SUPPORTED_AUDIO_FORMATS
    
    @property
    def weight(self) -> int:
        return self.discord_attachment.size
    
    @property
    async def content(self) -> bytes:
        return await self.discord_attachment.read(use_cached=True)

class DiscordChannel(Channel):
    discord_channel: discord.TextChannel
    client: discord.Client
    
    def __init__(self, client: discord.Client, channel: discord.TextChannel):
        self.discord_channel = channel
        self.client = client
        
        super().__init__ \
        (
            id = str(self.discord_channel.id),
            name = self.discord_channel.name,
        )
    
    @classmethod
    async def from_id(cls, bot: BotBase, id: str) -> 'DiscordChannel':
        from botter.discord import DiscordBot
        bot: DiscordBot
        return DiscordChannel(bot.client, await bot.client.fetch_channel(int(id)))
    
    async def fetch_message(self, id: str) -> 'DiscordMessage':
        return DiscordMessage(self.client, await self.discord_channel.fetch_message(int(id)))
    
    async def send_message(self, message: 'Message'):
        await send_message(self.discord_channel, message)
    
    async def send_typing(self, enabled: bool = True):
        if (not enabled):
            # Explicitly ignore case 'enabled == False'
            pass
        else:
            await self.discord_channel.trigger_typing()

class DiscordMessage(InboundMessage):
    discord_message: discord.Message
    client: discord.Client
    author: DiscordUser
    channel: DiscordChannel
    mentions: List[DiscordUser]
    
    def __init__(self, client: discord.Client, message: discord.Message):
        self.discord_message = message
        self.client = client
        
        attachments = self.discord_message.attachments
        super().__init__ \
        (
            id = str(self.discord_message.id),
            text = self.discord_message.content,
            attachments = [ DiscordAttachment(client, att) for att in attachments ],
            author = DiscordUser(client, self.discord_message.author),
            channel = DiscordChannel(client, self.discord_message.channel),
            mentions = [ DiscordUser(client, u) for u in message.mentions ],
        )
    
    @classmethod
    async def from_id(cls, channel: DiscordChannel, id: str) -> 'DiscordMessage':
        return await channel.fetch_message(id)
    
    async def reply(self, message: Message):
        await self.channel.send_message(replace(message, text=f"{self.author.discord_user.mention}\n{message.text}"))
    
    async def edit(self, new_text: str):
        await self.discord_message.edit(content=new_text)
    
    async def delete(self):
        await self.discord_message.delete()

async def send_message(channel: discord.TextChannel, message: Message):
    text = message.text.strip()
    files = [ (await at.temp_file, at.filename) for at in message.attachments]
    await channel.send(text or None, files = [ discord.File(*f) for f in files ])
    for loc, _ in files:
        safe_remove(loc)

__all__ = \
[
    'SUPPORTED_AUDIO_FORMATS',
    'DiscordAttachment',
    'DiscordChannel',
    'DiscordMessage',
    'DiscordUser',
    
    'send_message',
]

__pdoc_extras__ = \
[
    'SUPPORTED_AUDIO_FORMATS'
]
