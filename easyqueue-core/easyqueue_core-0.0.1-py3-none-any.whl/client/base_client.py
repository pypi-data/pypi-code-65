import copy
import http
import os
import time
import requests
from easyqueue.utils.validation import TypeValidator

from easyqueue.enums.RestProtocols import RestProtocols


class BaseClient:

    HTTP_PROXY_LOWER = 'http_proxy'
    HTTPS_PROXY_LOWER = 'https_proxy'
    HTTP_PROXY_UPPER = 'HTTP_PROXY'
    HTTPS_PROXY_UPPER = 'HTTPS_PROXY'

    MIN_PORT = 1024
    MAX_PORT = 49151

    DEBUG_TRACE_LIMIT: int = 20
    __supported_protocols: list = [RestProtocols.HTTP.value, RestProtocols.HTTPS.value]

    def __init__(self, host: str, port: int = None, protocol: str = RestProtocols.HTTP.value,
                 verify: bool = False, timeout: int = None, proxies: dict = None):
        self.__validate_init_args(host=host, port=port, protocol=protocol, timeout=timeout, proxies=proxies)
        self.__host = host
        self.__port = port
        self.__protocol = protocol
        self.__verify = verify
        self.__timeout = timeout
        self.__proxies = proxies
        self.__debug_trace = []
        self.__load_proxies_automatically()

    def __validate_init_args(self, host: str, port: int, protocol: str, timeout: int, proxies: dict):
        self.__validate_host(host=host)
        self.__validate_port(port=port)
        self.__validate_protocol(protocol=protocol)
        self.__validate_timeout(timeout=timeout)
        self.__validate_proxies(proxies=proxies)

    @property
    def host(self):
        return self.__host

    @staticmethod
    def __validate_host(host: str):
        TypeValidator.raise_validation_element_type(element_name='host', element=host, type_class=str, allow_none=False)
        TypeValidator.raise_validation_element_empty(element_name='host', element=host)

    @property
    def port(self):
        return self.__port

    @staticmethod
    def __validate_port(port: int):
        TypeValidator.raise_validation_element_type(element_name='port', element=port, type_class=int, allow_none=True)
        if port is not None:
            if port <= BaseClient.MIN_PORT or port > BaseClient.MAX_PORT:
                raise TypeError('Port must be between {} and {}'.format(BaseClient.MIN_PORT, BaseClient.MAX_PORT))

    @property
    def hostport(self):
        hostport = self.host
        if self.port is not None:
            hostport += ':{}'.format(self.port)
        return hostport

    @property
    def timeout(self):
        return self.__timeout

    @staticmethod
    def __validate_timeout(timeout: int):
        TypeValidator.raise_validation_element_type(
            element_name='timeout', element=timeout, type_class=int, allow_none=True)

    @timeout.setter
    def timeout(self, timeout: int):
        self.__validate_timeout(timeout=timeout)
        self.__timeout = timeout

    @property
    def proxies(self):
        return self.__proxies

    @staticmethod
    def __validate_proxies(proxies: dict):
        TypeValidator.raise_validation_element_type(
            element_name='proxies', element=proxies, type_class=dict, allow_none=True)
        if proxies:
            proxy_keys = proxies.keys()
            supported_keys = {BaseClient.HTTP_PROXY_LOWER, BaseClient.HTTPS_PROXY_LOWER}
            if len(proxy_keys > 2):
                raise TypeError('Invalid inputs proxies, more than two keys found. Allowed "http" and "https" only')

            for key in proxy_keys:
                if key not in supported_keys:
                    raise TypeError('Invalid inputs proxies, invalid key found. Allowed "http" and "https" only')

    @proxies.setter
    def proxies(self, proxies: dict):
        self.__validate_proxies(proxies=proxies)
        self.__proxies = proxies

    @property
    def protocol(self):
        return self.__protocol

    @staticmethod
    def __validate_protocol(protocol: str):
        supported_protocol_values = {str(p) for p in BaseClient.__supported_protocols}
        TypeValidator.raise_validation_element_type(
            element_name='protocol', element=protocol, type_class=str, allow_none=False)

        protocol = protocol.lower()
        if protocol not in supported_protocol_values:
            raise ValueError('Not supported protocol, must be among {}'.format(supported_protocol_values))

    @protocol.setter
    def protocol(self, protocol):
        self.__validate_protocol(protocol=protocol)
        if protocol == RestProtocols.HTTPS.value:
            self.__protocol = protocol
        else:
            self.__protocol = RestProtocols.HTTP.value
            self.verify = False

    @property
    def verify(self):
        return self.__verify

    @verify.setter
    def verify(self, verify):
        if self.protocol == RestProtocols.HTTPS.value:
            self.__verify = bool(verify)
        else:
            self.__verify = False

    @property
    def debug_trace(self):
        return copy.deepcopy(self.__debug_trace)

    def add_to_debug_trace(self, msg):
        to_add = '[{}] {}'.format(time.ctime(), msg)
        if len(self.__debug_trace) == self.DEBUG_TRACE_LIMIT:
            self.__debug_trace.pop()
        self.__debug_trace.append(to_add)

    @staticmethod
    def is_correct_status_code(status_code):
        TypeValidator.raise_validation_element_type(
            element_name='status_code', element=status_code, type_class=int, allow_none=False)
        return http.HTTPStatus.OK.value <= status_code < http.HTTPStatus.MULTIPLE_CHOICES.value

    def __load_proxies_automatically(self):
        proxies = {}
        os_keys = os.environ.keys()
        if self.HTTP_PROXY_LOWER in os_keys:
            proxies[RestProtocols.HTTP.value] = os.environ[ self.HTTP_PROXY_LOWER]
        elif self.HTTP_PROXY_UPPER in os_keys:
            proxies[RestProtocols.HTTP.value] = os.environ[self.HTTP_PROXY_UPPER]

        if self.HTTPS_PROXY_LOWER in os_keys:
            proxies[RestProtocols.HTTPS.value] = os.environ[self.HTTPS_PROXY_LOWER]
        elif self.HTTPS_PROXY_UPPER in os_keys:
            proxies[RestProtocols.HTTPS.value] = os.environ[self.HTTPS_PROXY_UPPER]

        if proxies != {}:
            self.add_to_debug_trace('Detected proxies: {}'.format(proxies))
            self.__proxies = proxies

    def call(self, method, url, headers=None, params=None, body=None, data=None):
        method = method.upper()
        self.add_to_debug_trace('Calling rest api, method:{}, url:{}, headers:{}, params:{}'
                                .format(method, url, headers, params))
        response = requests.request(method, url, headers=headers, params=params, json=body, data=data,
                                    verify=self.verify, timeout=self.timeout, proxies=self.proxies)
        self.add_to_debug_trace('Call rest api response: {}'.format(response))

        return response
