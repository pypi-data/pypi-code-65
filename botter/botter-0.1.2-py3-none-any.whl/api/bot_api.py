import os
from dataclasses import dataclass, field
from enum import Enum, auto
from tempfile import mkstemp
from typing import *
from uuid import uuid4

from .bot_base import BotBase

@dataclass(frozen=True)
class User:
    id: str
    user_name: str = field(compare=False)
    display_name: str = field(compare=False)

class AttachmentType(Enum):
    """
    An enum representing an attachment type.
    It is not guaranteed that new attachment types won't be available in the future,
    so this list is incomplete.
    
    However, it is stated **all** officially supported platforms
    could work correctly with the attachment types represented in this list.
    """
    
    Image = auto()
    """
    All image data types, including photos, stickers, GIF-images and the others.
    """
    
    Audio = auto()
    """
    All audio data types, including songs, voice messages, TTS and the others.    
    """
    
    Video = auto()
    """
    All video data types, in any supported format (usually .mp4).    
    """
    
    Document = auto()
    """
    All attachments those are not classified by the other categories.    
    """

@dataclass
class Attachment:
    """
    Attachment class.
    
    This represents an abstract, platform-independent file reference,
    with the metadata and ability to download/upload available.
    
    This class is used for both bot->server uploads and server->bot downloads.
    """
    
    id: str
    type: AttachmentType
    """
    Attachment type.
    See `AttachmentType` description for details.
    """
    
    filename: str
    """
    Attachment filename provided by the platform.
    Usually it is a filename used during the upload,
    rarer - the file ID with an extension.
    """
    
    _tmp_file: str = field(repr=False, default=None, init=False)
    @property
    async def temp_file(self) -> str:
        """
        Returns a path to a temporary file with attachment content.
        You should never use this property with the regular files,
        as they can be easily deleted by the program.
        
        :return: Awaitable[str]
        """
        
        if (self._tmp_file is not None):
            if (os.path.isfile(self._tmp_file)):
                return self._tmp_file
        
        fd, path = mkstemp(suffix='.' + self.filename)
        with os.fdopen(fd, 'wb') as f:
            f.write(await self.content)
        self._tmp_file = path
        return path
    
    @property
    async def content(self) -> bytes:
        """
        Asynchronously returns attachment content as bytes.
        
        :return: Awaitable[bytes]
        """
        
        raise NotImplementedError
    
    @property
    def weight(self) -> int:
        """
        Attachment size in bytes.
        
        :return: int
        """
        
        raise NotImplementedError

@dataclass
class InMemoryAttachment(Attachment):
    """
    Represents an attachment that is stored in the memory.
    """
    
    id: str = field(init=False, default_factory=uuid4)
    extension: str = field(default=None)
    filename: str = field(default=None)
    _content: bytes = field(default=None)
    
    def __post_init__(self):
        if (self.filename is None):
            self.filename = f'image-query.{self.extension}'
    
    @property
    def weight(self) -> int:
        return len(self._content)
    
    @property
    async def content(self) -> bytes:
        return self._content

@dataclass
class FileAttachment(Attachment):
    """
    Represents an attachment that is stored in local file,
    usually used for file upload.
    """
    
    path: str
    """
    A path to the local file.
    File must exist and be valid and readable for current user.
    """
    
    id: str = field(init=False, default=None)
    filename: str = field(init=False, default=None)
    
    def __post_init__(self):
        if (self.id is None):
            self.id = str(hash(self.path))
        if (self.filename is None):
            self.filename = os.path.basename(self.path)
    
    @property
    def weight(self) -> int:
        return os.path.getsize(self.path)
    
    @property
    async def content(self) -> bytes:
        with open(self.path, 'rb') as f:
            return f.read()

@dataclass(frozen=True)
class Channel:
    id: str = None
    name: str = None
    
    def __post_init__(self):
        if (self.id is None):
            raise ValueError("Field 'id' is mandatory!")
        if (self.name is None):
            raise ValueError("Field 'name' is mandatory!")
    
    @classmethod
    async def from_id(cls, bot: BotBase, channel_id: str) -> 'Channel':
        raise NotImplementedError
    
    async def fetch_message(self, id: str) -> 'InboundMessage':
        raise NotImplementedError
    async def send_message(self, message: 'Message'):
        raise NotImplementedError
    async def send_typing(self, enabled: bool = True):
        raise NotImplementedError

@dataclass(frozen=True)
class Message:
    text: str
    attachments: List[Attachment] = field(default_factory=list)
    
    @property
    def has_attachments(self) -> bool:
        return len(self.attachments) > 0
    @property
    def has_image(self) -> bool:
        return any(at.type == AttachmentType.Image for at in self.attachments)

@dataclass(frozen=True)
class InboundMessage(Message):
    id: str = None
    author: User = None
    channel: Channel = None
    mentions: List[User] = field(default_factory=list)
    
    def __post_init__(self):
        if (self.id is None):
            raise ValueError("Field 'id' is mandatory!")
        if (self.author is None):
            raise ValueError("Field 'author' is mandatory!")
        if (self.channel is None):
            raise ValueError("Field 'channel' is mandatory!")
    
    @classmethod
    async def from_id(cls, channel: Channel, id: str) -> 'InboundMessage':
        raise NotImplementedError
    
    async def reply(self, message: Message):
        raise NotImplementedError
    async def edit(self, new_text: str):
        raise NotImplementedError
    async def delete(self):
        raise NotImplementedError

__all__ = \
[
    'Attachment',
    'AttachmentType',
    'Channel',
    'FileAttachment',
    'InboundMessage',
    'InMemoryAttachment',
    'Message',
    'User',
]
