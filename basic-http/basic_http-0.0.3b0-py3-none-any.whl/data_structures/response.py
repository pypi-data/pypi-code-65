from basic_http.util.response_parser import parse_http_response
import basic_http.exceptions.structures
import basic_http.exceptions.http_reader
from basic_http.util.networking import HttpSocketReader


class HttpResponse(object):
    def __init__(self, data: bytes = None):
        self.__data = None

        if data:
            self.load(data)

    def __str__(self):
        response_line = self.__data['response_line']
        response_line = f'{response_line["http_protocol"]} {response_line["status_code"]} {response_line["status"]}'
        return response_line + '\n' + str(self.__data['header']) + '\n\n' + str(self.__data['body'])

    def load(self, data: bytes):
        try:
            self.__data = parse_http_response(data)
        except Exception:
            raise basic_http.exceptions.http_reader.InvalidHttpResponse('Remote host sent an invalid response.')

    def content_length(self):
        content_length = 0

        if not self.__data:
            return content_length

        try:
            return int(self.__data['header']['Content-Length'])
        except basic_http.exceptions.structures.KeyNotFound:
            if self.__data['body']:
                return len(self.__data['body'])
            else:
                return 0

    def status(self):
        return self.__data['response_line']['status']

    def status_code(self):
        return self.__data['response_line']['status_code']

    def get_header(self):
        return self.__data['header']

    def body(self):
        return self.__data['body']

    def append_to_body(self, data: bytes):
        self.__data['body'] += data

    def receive(self, connection):
        http_socket_reader = HttpSocketReader(connection)
        self.__data = http_socket_reader.read()
