import ssl
import socket
import urllib.parse
from copy import deepcopy
from basic_http.util.networking import is_ip_address
from basic_http.data_structures.request import HttpRequest
from basic_http.data_structures.response import HttpResponse


class Connection(object):
    def __init__(self):
        self.__connection = dict()
        self.__proxy = dict()

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        connection_details = dict()
        details = dict()

        socket_object = self.__connection['socket']
        socket_details = {
            'fd': str(socket_object.fileno()),
            'family': str(socket_object.family),
            'type': str(socket_object.type),
            'laddr': socket_object.getsockname(),
            'raddr': socket_object.getpeername()
        }

        for key, value in self.__connection.items():
            if key == 'socket':
                connection_details['socket'] = socket_details
            else:
                connection_details[key] = value

        details.update({
            'connection': connection_details,
            'proxy': deepcopy(self.__proxy)
        })
        # print(details)
        return connection_details

    @staticmethod
    def __connect(host: str, port: str):
        connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        addr_info = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, 0)

        for addr in addr_info:
            address = addr[-1]
            try:
                connection_socket.connect(address)
                break
            except Exception:
                pass
        else:
            raise Exception('Cannot connect to host')
        return connection_socket

    def __connect_proxy(self, host):
        sock = self.__connect(self.__proxy['host'], self.__proxy['port'])

        if self.__proxy['scheme'] == 'https':
            ssl_context = ssl.SSLContext()
            sock = ssl_context.wrap_socket(sock)
            sock.do_handshake()

        request = HttpRequest()
        request.method = 'CONNECT'
        request.path = host
        request.header.add({
            'Proxy-Connection': 'keep-alive',
            'Connection': 'keep-alive',
            'Host': host
        })

        request.send(sock)

        response = HttpResponse()
        response.receive(sock)

        return sock, response.status_code(), response.status()

    def __error(self, error: str):
        self.__connection['error'] = error

    def __busy(self, busy: bool):
        self.__connection['busy'] = busy

    def connect(self, host: str, port: str, scheme: str = 'http'):
        if self.is_connected() and self.get_host() == host + ':' + port:
            return True

        self.__connection.update({
            'scheme': None,
            'host': None,
            'socket': None,
            'connected': False,
            'error': None,
            'busy': False
        })

        address = host + ':' + port
        proxy = self.get_proxy()

        if proxy:
            try:
                sock, status_code, status = self.__connect_proxy(address)
            except Exception as exception:
                self.__error(f'Proxy connection failed: { exception }.')
                return False

            if status_code not in range(200, 300):
                self.__error(f'Proxy server responded with status: { status }.')
                return False
        else:
            try:
                sock = self.__connect(host, port)
            except Exception as exception:
                self.__error(f'Connection to { address } failed: { exception }.')
                return False

        if scheme == 'https':
            try:
                ssl_context = ssl.SSLContext()
                sock = ssl_context.wrap_socket(sock)
                sock.do_handshake()
            except Exception as exception:
                self.__error(f'Https connection to { address } failed: { exception }.')
                return False

        self.__connection.update({
            'scheme': scheme,
            'host': address,
            'socket': sock,
            'connected': True,
        })

        return True

    def set_proxy(self, proxy_address: str):
        parsed = urllib.parse.urlparse(proxy_address)
        host = parsed.netloc
        port = '80'

        if ':' in host:
            host, port = host.split(':', 1)

        self.__proxy = {
            'host': host,
            'port': port,
            'scheme': parsed.scheme
        }

    def send(self, data: bytes):
        self.__busy(True)
        bytes_sent = None

        try:
            bytes_sent = self.get_socket().send(data)
        except Exception as exception:
            self.__error(f'Error sending data: { exception }.')
        finally:
            self.__busy(False)

        return bytes_sent

    def receive(self):
        response = None
        try:
            self.__busy(True)
            return self.get_socket().recv(1024 * 10)
        except Exception as exception:
            self.__error(f'Remote host closed connection: { exception }.')
        finally:
            self.__busy(False)

        return response

    def get_proxy(self):
        return self.__proxy

    def get_socket(self):
        try:
            return self.__connection['socket']
        except KeyError:
            return None

    def is_connected(self):
        try:
            return self.__connection['connected']
        except KeyError:
            return False

    def get_host(self):
        try:
            return self.__connection['host']
        except KeyError:
            return ''

    def get_domain(self):
        host = self.get_host()
        if ':' in host:
            host = host.split(':')[0]

        if is_ip_address(host):
            return host

        return '.'.join(host.split('.')[-2:])

    def is_busy(self):
        try:
            return self.__connection['busy']
        except KeyError:
            return False

    def get_last_error(self):
        try:
            return self.__connection['error']
        except KeyError:
            return ''

    def close(self):
        sock = self.get_socket()
        if sock:
            sock.close()
        self.__connection.update({
            'connected': False,
            'busy': False
        })
