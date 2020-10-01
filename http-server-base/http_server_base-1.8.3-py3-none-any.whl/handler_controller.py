from typing import *

from tornado.web import RequestHandler, Application
from typing.re import *

# noinspection PyTypeChecker
P = TypeVar('P', str, Pattern[str])
HandlerType = Union[Tuple[P, Type[RequestHandler]], Tuple[P, Type[RequestHandler], Dict[str, Any]]]
HandlerListType = List[HandlerType]

class HandlerController:
    base_path: str
    application: Application = None
    
    handlers: HandlerListType = list()
    
    def __init__(self, application: Application):
        self.application = application
    
    def get_self_handlers(self) -> HandlerListType:
        return self.handlers

__all__ = \
[
    'HandlerType',
    'HandlerListType',
    'HandlerController',
]
__pdoc_extras__ = \
[
    'HandlerType',
    'HandlerListType',
]
