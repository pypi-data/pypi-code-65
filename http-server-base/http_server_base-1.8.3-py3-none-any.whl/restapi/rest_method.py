from typing import Callable, Pattern

from http_server_base import Logged_RequestHandler
from .extras import CanonicalArgumentListType

class RestMethod:
    name: str
    path: str
    listen_re: Pattern[str]
    
    query_arguments: CanonicalArgumentListType
    body_arguments: CanonicalArgumentListType
    path_arguments: CanonicalArgumentListType
    header_arguments: CanonicalArgumentListType
    
    action: Callable
    
    def invoke(self, handler: Logged_RequestHandler):
        pass

__all__ = \
[
    'RestMethod',
]
