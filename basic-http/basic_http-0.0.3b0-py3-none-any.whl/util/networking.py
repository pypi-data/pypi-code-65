import string
import random
import urllib.parse
import basic_http.exceptions.structures
import basic_http.exceptions.http_reader
from basic_http.util.response_parser import parse_http_response


def generate_websocket_key():
    chars = string.ascii_letters + '0123456789'
    stop_range = len(chars) - 1
    return ''.join([chars[random.randint(0, stop_range)] for k in range(22)]) + '=='


def is_ip_address(host: str):
    if ':' in host:
        host = host.split(':', 1)[0]
    tokens = host.split('.')

    if len(tokens) != 4:
        return False

    for token in tokens:
        if not token.isdecimal():
            return False

        if not 0 <= int(token) <= 255:
            return False

    return True


def get_details(url: str):
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    scheme = parsed_url.scheme
    path = url.split(host)[-1]
    query = parsed_url.query

    if ':' in host:
        host, port = host.split(':', 1)
    elif scheme == 'http':
        port = '80'
    elif scheme == 'https':
        port = '443'
    else:
        raise Exception(f'Unknown request scheme: {scheme}.')

    return {
        'scheme': scheme,
        'host': host,
        'port': port,
        'path': path,
        'query': query
    }


class HttpSocketReader:
    def __init__(self, connection):
        self.__connection = connection

    def read_once(self):
        return self.__connection.receive()

    def read(self):
        partial_data = self.read_once()
        # print(partial_data)

        try:
            partial_parsed_data = parse_http_response(partial_data)
        except Exception:
            raise basic_http.exceptions.http_reader.InvalidHttpResponse('Remote host sent an invalid response.')

        http_header = partial_parsed_data['header']
        partial_body = partial_parsed_data['body']

        try:
            transfer_encoding_header = http_header.get_all_header('Transfer-Encoding')
        except basic_http.exceptions.structures.KeyNotFound:
            transfer_encoding_header = None

        try:
            content_length = int(http_header['Content-Length'])
        except basic_http.exceptions.structures.KeyNotFound:
            content_length = None

        chunked = False
        for instance in transfer_encoding_header:
            if 'chunked' in instance:
                chunked = True
                break

        if not chunked and not content_length:
            return partial_parsed_data

        partial_body_lenth = len(partial_body)

        if content_length and partial_body_lenth >= content_length:
            return partial_parsed_data

        while True:
            try:
                # print('reading...')
                data = self.read_once()
                # print('data:', data)
            except Exception as exception:
                raise basic_http.exceptions.http_reader.\
                    HttpReaderError(f'Remote host closed connection: {exception}')

            partial_parsed_data['body'] += data
            partial_body_lenth += len(data)
            # print('content-lenght:', partial_body_lenth)

            if (chunked and data[-5:] == b'0\r\n\r\n') or (content_length and content_length <= partial_body_lenth):
                break

        return partial_parsed_data
