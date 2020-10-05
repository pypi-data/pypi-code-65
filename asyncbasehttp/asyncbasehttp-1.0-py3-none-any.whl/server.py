# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import logging
from abc import abstractmethod, ABCMeta
from asyncio import BaseTransport, StreamWriter, StreamReader, IncompleteReadError, LimitOverrunError
from enum import Enum, auto
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from typing import Optional, Awaitable, Callable

__all__ = (
        'Response',
        'Request',
        'PreProcessResponse',
        'RequestHandler',
        'request_handler',
        'HTTP_HEADER_SUFFIX',
        )

HTTP_HEADER_SUFFIX = b'\r\n\r\n'

logger = logging.getLogger(__name__)


class Response:
    def __init__(self, status: HTTPStatus, message: str = None):
        self.status = status
        self.message = message
        self.headers = []
        self.body = BytesIO()
        self.cookies = SimpleCookie()

    def add_header(self, keyword, value):
        self.headers.append((keyword, value))

    def add_cookie(self, keyword, value):
        self.cookies[keyword] = value

    def write_body(self, data: bytes):
        self.body.write(data)

    @classmethod
    def create_ok_response(cls, data: bytes):
        response = cls(HTTPStatus.OK)
        response.headers = [('Content-Length', str(len(data)))]
        response.body = BytesIO(data)
        return response

    @classmethod
    def no_body_response(cls, status: HTTPStatus, message: str = None):
        response = cls(status, message)
        response.headers = [('Content-Length', "0")]
        return response


class Request:
    def __init__(self, reader: StreamReader, writer: StreamWriter, internal_request: 'RequestInternal'):
        self.reader = reader
        self.writer = writer
        self.internal_request = internal_request
        self._keep_alive = True

    @property
    def headers(self):
        return self.internal_request.headers

    @property
    def command(self):
        return self.internal_request.command

    @property
    def path(self):
        return self.internal_request.path

    @property
    def requestline(self):
        return self.internal_request.requestline

    @property
    def request_version(self):
        return self.internal_request.request_version

    @property
    def keep_alive(self):
        return self._keep_alive and self.internal_request.rfile.was_read_fully

    async def get_body(self):
        content_len = int(self.headers.get('Content-Length', 0))
        return await self.reader.read(content_len)

    async def json(self):
        return json.loads(await self.get_body())

    def force_close(self):
        self._keep_alive = False

    async def send_response_headers(self, response: Response):
        self.internal_request.send_response(response.status, response.message)
        self.internal_request.send_headers(response.headers)
        self.internal_request.send_cookies(response.cookies)
        self.internal_request.end_headers()
        await self.flush_header_buffer()

    def header_buffer(self):
        return self.internal_request.wfile.data

    async def flush_header_buffer(self):
        for line in self.internal_request.wfile.data:
            self.writer.write(line)
        await self.writer.drain()
        self.internal_request.wfile = WFile()


class PreProcessResponse(Enum):
    NO_BUFFER = auto()
    PARTIAL_BUFFER = auto()
    FULL_BUFFER = auto()
    CLOSE = auto()
    SKIP_TO_NEXT = auto()


class RequestHandler(metaclass=ABCMeta):

    @abstractmethod
    async def process_request(self, request: Request) -> Optional[Response]:
        """ The callback for user code """
        pass

    # noinspection PyMethodMayBeStatic
    async def pre_process_request(self, _: StreamReader, __: StreamWriter) -> (PreProcessResponse, Optional[bytes]):
        """
        Allows user code to peek before actually doing anything.
        Use cases:
        1) Do the entire processing here. E.g. If the server is from a trusted source, skip header processing and
           go to content
        2) Fast spam control. E.g. Just read the first line and if it does not match 'GET /my_secret_path', reject.

        Return PreProcessResponse and the header buffer consumed by user code
        """
        return PreProcessResponse.NO_BUFFER, None

    # noinspection PyMethodMayBeStatic
    async def new_client(self, transport: BaseTransport) -> bool:
        """
        Callback called when a new connection is made
        Use cases:
        1) Reject client based on address
        2) Profiling

        Return True to process requests from the connection
        """
        logger.debug("New client: %s", _get_client_address(transport))
        return True

    # noinspection PyMethodMayBeStatic
    async def client_left(self, transport: BaseTransport) -> None:
        """
        Callback called when a connection is closed
        """
        logger.debug("Client left: %s", _get_client_address(transport))

    # noinspection PyMethodMayBeStatic
    async def process_protocol_error(self, request: Request) -> bool:
        """ 
        HTTP protocol level error. 
        Default implementation does the expected graceful responses.

        Return True to continue processing further requests from client
        """
        logger.debug("Protocol Error")
        await request.flush_header_buffer()
        return False

    # noinspection PyMethodMayBeStatic
    async def process_transport_error(self, ex: Exception) -> bool:
        """
        Transport level error for e.g. a very large request

        Return True to continue processing further requests from client
        """
        logger.debug("Transport error", ex)
        return False

    async def __call__(self, reader: StreamReader, writer: StreamWriter):
        await _handle(self, reader, writer)


HandleRequestCB = Callable[['Request'], Awaitable[Optional[Response]]]


def request_handler(func: HandleRequestCB) -> RequestHandler:
    class UserRequestHandler(RequestHandler):
        async def process_request(self, request: Request) -> Optional[Response]:
            return await func(request)

    return UserRequestHandler()


def _get_client_address(transport: BaseTransport):
    return transport.get_extra_info('peername')


async def _pre_process_request(handler, reader: StreamReader, writer: StreamWriter) -> (Optional[bytes], bool):
    response, header_buffer = await handler.pre_process_request(reader, writer)

    if response is PreProcessResponse.CLOSE:
        return None, False
    elif response is PreProcessResponse.SKIP_TO_NEXT:
        return None, True

    try:
        if response is PreProcessResponse.NO_BUFFER:
            return await reader.readuntil(HTTP_HEADER_SUFFIX), True
        elif response is PreProcessResponse.PARTIAL_BUFFER:
            return header_buffer + await reader.readuntil(HTTP_HEADER_SUFFIX), True
        elif response is PreProcessResponse.FULL_BUFFER:
            pass
        else:
            raise ValueError(f"Not a valid PreProcessResponse:  {response}")
    except IncompleteReadError as ire:
        logger.debug(f'Got IncompleteReadError {ire}')
        return None, await handler.process_transport_error(ire)
    except LimitOverrunError as loe:
        return None, await handler.process_transport_error(loe)


async def _process_request(handler: RequestHandler, request: Request):
    response = await handler.process_request(request)
    if response:
        await request.send_response_headers(response)
        request.writer.write(response.body.read())

    await request.writer.drain()
    return request.keep_alive


async def _handle(handler: RequestHandler, reader: StreamReader, writer: StreamWriter):

    client_address = _get_client_address(writer.transport)
    logger.debug("New client connected. Client: %s", client_address)

    try:

        if not await handler.new_client(writer.transport):
            logger.debug("Client ignored by handler. Client: %s", client_address)
            return

        logger.debug('Starting to process requests. Client: %s', client_address)

        while True:

            header_buffer, should_continue = await _pre_process_request(handler, reader, writer)
            if not should_continue:
                break

            internal_request = RequestInternal(BytesIO(header_buffer), client_address)
            request = Request(reader, writer, internal_request)

            if request.internal_request.error:
                if not await handler.process_protocol_error(request):
                    break

            if not await _process_request(handler, request):
                break

        logger.debug('Done processing requests. Client: %s', client_address)

    finally:
        writer.close()
        # await writer.wait_closed()
        await handler.client_left(writer.transport)
        logger.debug('Done with client. Client: %s', client_address)


class RFile:
    def __init__(self, buffer: BytesIO):
        self.buffer = buffer
        self.was_read_fully = False

    def readline(self, *args, **kwargs):
        line = self.buffer.readline(*args, **kwargs)
        if not line:
            self.was_read_fully = True
        return line


class WFile:
    def __init__(self):
        self.data = []

    def write(self, data):
        self.data.append(data)

    @staticmethod
    def flush():
        pass


class RequestInternal(BaseHTTPRequestHandler):
    def __init__(self, buffer: BytesIO, client_address):
        self.rfile = RFile(buffer)
        self.wfile = WFile()
        self.error = True
        super().__init__(None, client_address, None)

    def setup(self):
        pass

    def finish(self):
        pass

    def handle_expect_100(self):
        return True

    def send_headers(self, headers):
        for keyword, value in headers:
            self.send_header(keyword, value)
        self.flush_headers()

    def send_cookies(self, cookies: SimpleCookie):
        if cookies:
            self.wfile.write(f"{cookies.output()}\r\n".encode())

    def __getattr__(self, item):
        if not item.startswith('do_'):
            raise AttributeError(item)

        def handle_method():
            self.error = False

        return handle_method

    protocol_version = "HTTP/1.1"
