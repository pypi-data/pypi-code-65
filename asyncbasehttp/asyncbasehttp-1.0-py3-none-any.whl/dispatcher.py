from enum import Enum, auto
from typing import Optional

from asyncbasehttp import Request, Response
from . import RequestHandler


class NextAction(Enum):
    DONE = auto()
    CONTINUE = auto()
    CLOSE = auto()


class Dispatcher(RequestHandler):
    def __init__(self):
        self.request_cbs = []

    async def process_request(self, request: Request) -> Optional[Response]:
        for cb in self.request_cbs:
            resp = cb(request)
            if isinstance(resp, Response):
                return resp
            elif resp is NextAction.DONE:
                return
            elif resp is NextAction.CONTINUE:
                continue
            elif resp is NextAction.CLOSE:
                request.force_close()

    def add_condition_cb(self, predicate, cb):
        def request_cb(request: Request):
            if predicate(request):
                return cb(request)
            else:
                return NextAction.CONTINUE

        self.request_cbs.append(request_cb)

    def add_path_cb(self, path, cb):
        def predicate(request: Request):
            return request.path == path
        self.add_condition_cb(predicate, cb)
