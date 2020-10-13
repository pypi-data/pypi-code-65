from typing import *

from ..util import NoReturn

T = TypeVar('T')
class BotBase(Generic[T]):
    implementation: Type[T] = None
    client: T = None
    
    def start(self) -> NoReturn:
        raise NotImplementedError
    
    @classmethod
    def run(cls, *args, **kwargs) -> NoReturn:
        raise NotImplementedError

__all__ = \
[
    'BotBase',
]
