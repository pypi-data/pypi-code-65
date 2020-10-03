from basic_http.data_structures.header import HttpHeader
from basic_http.util.forms import encode_multipart_formdata
import urllib.parse
import basic_http.exceptions.request_response


class HttpRequest(object):
    def __init__(self):
        self.http_version = 'HTTP/1.1'
        self.path = '/'
        self.method = 'GET'
        self.header = HttpHeader()
        self.body = ''
        self.charset = 'utf-8'

    def __bytes__(self) -> bytes:
        r = bytes(self.method + ' ' + self.path + ' ' + self.http_version + '\r\n' + str(self.header) + '\r\n',
                  self.charset)
        try:
            r += self.body
        except TypeError:
            r += bytes(self.body, self.charset)

        return r

    def __str__(self):
        try:
            return str(self.__bytes__(), self.charset)
        except Exception as exception:
            print('There was a problem converting HttpRequest object to string representation:', exception)

    def add_x_www_form_urlencode(self, data: dict):
        self.body = urllib.parse.urlencode(data)

    def add_multipart_form_data(self, files: dict):
        self.body, content_type = encode_multipart_formdata(files)
        self.header['Content-Type'] = content_type

    def content_length(self):
        return len(self.body)

    def send(self, connection):
        content_lenght = self.content_length()
        if content_lenght:
            self.header['Content-Length'] = str(content_lenght)

        request_buffer = self.__bytes__()
        request_buffsize = len(request_buffer)
        try:
            bytes_sent = connection.send(request_buffer)
        except Exception as exception:
            raise basic_http.exceptions.request_response.RequestSendError(f'Error sending request: {exception}')

        if request_buffsize != bytes_sent:
            print('There was a problem sending request: sent data size different from request buffer size.')

        return bytes_sent
