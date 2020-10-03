import urllib.parse
import time
import json

from basic_http.cookies.cookies import SessionCookiesKeeper
from basic_http.data_structures.request import HttpRequest
from basic_http.data_structures.response import HttpResponse
from basic_http.connection import Connection
from basic_http.util.networking import get_details
from basic_http.user_agents.user_agent import UserAgent
import basic_http.exceptions.session

LIB_VERSION = str()
DEFAULT_AGENT = str()


class HttpSession(object):
    def __init__(self, **kwargs):
        self.connection = Connection()
        self.cookies_enabled = True
        self.follow_redirects = True
        self.cookies_keeper = SessionCookiesKeeper()

        self.user_agent = DEFAULT_AGENT

        self.__requests_chain = list()
        self.__parse_user_config(**kwargs)

    def __str__(self):
        formated_json = json.dumps(self.to_dict(), indent=3)
        return formated_json.replace('\"', '\'')

    def __parse_user_config(self, **kwargs):
        if 'user_agent' in kwargs:
            self.user_agent = kwargs['user_agent']
        elif 'random_agent' in kwargs:
            ua = UserAgent()
            ua.pick_random(kwargs['random_agent'])
            self.user_agent = ua.get()

        if 'follow_redirects' in kwargs:
            self.follow_redirects = kwargs['follow_redirects']

        if 'cookies_enabld' in kwargs:
            self.cookies_enabled = kwargs['cookie_enabled']

    def __prepare_http_request(self, method, path, header, body, **kwargs):
        request = HttpRequest()
        request.method = method
        request.body = body

        if path:
            request.path = path

        if 'data' in kwargs and kwargs['data']:
            request.add_x_www_form_urlencode(kwargs['data'])

        if 'files' in kwargs and kwargs['files']:
            request.add_multipart_form_data(kwargs['files'])

        request.header.add({'User-Agent': self.user_agent})

        if header:
            request.header.update(header)

        request.header.add({
            'Connection': 'keep-alive',
            'cache-control': 'no-cache',
            'Accept': '*/*',
            'Host': self.connection.get_host(),
        })

        return request

    def __get_cookies_from_response(self, response, url):
        if not self.cookies_enabled:
            return

        header = response.get_header()
        for instance in header.get_cookies():
            self.cookies_keeper.update(instance, url)

    def __get_request_cookies(self, url: str):
        if not self.cookies_enabled:
            return None

        return self.cookies_keeper.cookie_header(url)

    def to_dict(self):
        details = dict(self.connection.to_dict())
        details.update({
            'cookie_enabled': self.cookies_enabled,
            'cookies': self.get_cookies()
        })
        return details

    def set_proxy(self, proxy_address):
        self.connection.set_proxy(proxy_address)

    def get_proxy(self):
        return self.connection.get_proxy()

    def get_cookies(self):
        return self.cookies_keeper.get_all_as_dir()

    def clear_cookies(self):
        self.cookies_keeper.clear()

    def is_connected(self):
        return self.connection.is_connected()

    def connection_socket(self):
        return self.connection.get_socket()

    def use_cookies(self, use_cookies: bool):
        self.cookies_enabled = use_cookies

    def create_connection(self, host: str, port: str, scheme: str = 'http'):
        result = self.connection.connect(host, port, scheme)
        self.cookies_keeper.set_domain(self.connection.get_domain())
        return result

    def request(self, method: str, url: str, header=None, raw_body: str = '', **kwargs):
        self.__requests_chain = list()
        scheme, host, port, path, query = get_details(url).values()

        if not self.create_connection(host, port, scheme):
            raise basic_http.exceptions.session.HostUnreachable(f'Host unreachable: {host}:{port}')

        request = self.__prepare_http_request(method, path, header, raw_body, **kwargs)
        cookies = self.__get_request_cookies(url)

        if cookies:
            request.header.update({
                'Cookie': cookies
            })

        request.send(self.connection)

        response = HttpResponse()
        response.receive(self.connection)

        self.__get_cookies_from_response(response, url)

        if response.status_code() in range(300, 400) and self.follow_redirects:
            location = response.get_header()['location']
            self.request(method, location, header, raw_body, **kwargs)

        self.__requests_chain.insert(0, (request, response))

        return self.__requests_chain[-1][1]

    def close(self):
        self.connection.close()

    def busy(self):
        return self.connection.is_busy()

    def get_requests_chain(self):
        return self.__requests_chain
