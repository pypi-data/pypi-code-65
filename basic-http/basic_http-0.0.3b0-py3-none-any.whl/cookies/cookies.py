import urllib.parse
import basic_http.exceptions.cookies
import basic_http.cookies.cookies_util


class Cookie(object):
    def __init__(self, ignore_bad_cookie: bool = False):
        self.__cookie = dict()
        self.__ignore_bad_cookie = ignore_bad_cookie
        self.__host_only_cookie = False

    def update(self, data, request_url: str = None):
        if isinstance(data, str):
            self.__cookie.update(basic_http.cookies.cookies_util.parse_cookie(data, self.__ignore_bad_cookie))
        elif isinstance(data, dict):
            self.__cookie.update(data)

        parsed_url = urllib.parse.urlparse(request_url)

        if (not self.domain() or not self.path()) and not request_url:
            raise basic_http.exceptions.cookies.BadCookie('Cookie domain and/or path unknown.')

        if not self.domain():
            self['domain'] = parsed_url.netloc.split(':')[0]
            self.__host_only_cookie = True

        if not self.path():
            path = parsed_url.path

            if not path:
                path = '/'

            self['path'] = path

    def name(self):
        return self['name']

    def value(self):
        return self['value']

    def domain(self):
        return self['domain']

    def path(self):
        return self['path']

    def match_domain(self, domain: str):
        cookie_domain = self.domain()
        if self.__host_only_cookie and cookie_domain != domain:
            return False

        cookie_domain = cookie_domain.strip('.')
        cookie_domain_tokens = cookie_domain.split('.')
        domain_tokens = domain.split('.')

        if len(cookie_domain_tokens) > len(domain_tokens):
            return False

        cookie_domain_tokens.reverse()
        domain_tokens.reverse()

        return False not in map(lambda x, y: x == y, cookie_domain_tokens, domain_tokens)

    def match_path(self, path: str):
        cookie_path = self.path()
        if cookie_path == '/':
            return True

        cookie_path = cookie_path.strip('/')
        path = path.strip('/')

        cookie_path_tokens = cookie_path.split('/')
        path_tokens = path.split('/')

        return False not in map(lambda x, y: x == y, cookie_path_tokens, path_tokens)

    def match_url(self, url: str):
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.split(':')[0]
        path = parsed_url.path

        if not path:
            path = '/'

        return self.match_domain(domain) and self.match_path(path)

    def needs_update(self, new_cookie):
        if new_cookie.name() != self.name():
            return False

        if self.path().strip('/') != new_cookie.path().strip('/'):
            return False

        if self.domain().strip('.') != new_cookie.domain().strip('.'):
            return False

        return True

    def __str__(self):
        cookie = ''
        if self.__cookie:
            cookie += self.__cookie['name'] + '=' + self.__cookie['value']
            for attribute in basic_http.cookies.cookies_util.valid_attributes:
                try:
                    cookie += f'; { attribute }={ self.__cookie[attribute] }'
                except KeyError:
                    pass
        return cookie

    def __getitem__(self, item: str):
        for key, value in self.__cookie.items():
            if key.lower() == item.lower():
                return value
        return ''

    def __setitem__(self, key: str, value: str):
        if not self.__ignore_bad_cookie and \
                key.lower() not in basic_http.cookies.cookies_util.valid_attributes + ['name', 'value']:
            raise AttributeError(f'Wrong cookie attribute: { key }.')

        for _key, _value in self.__cookie.items():
            if key.lower() == _key.lower():
                self.__cookie[_key] = value
                break
        else:
            self.__cookie[key] = value

    def __iter__(self):
        for item in self.__cookie.items():
            yield item


class SessionCookiesKeeper:
    def __init__(self, domain: str = None, ignore_bad_cookies: bool = False):
        self.__ignore_bad_cookies = ignore_bad_cookies
        self.__cookies = list()
        self.__domain = domain

    def update(self, header_data: str, url: str = None):
        parsed_cookies = basic_http.cookies.cookies_util.parse_set_cookie_header(header_data, self.__ignore_bad_cookies)
        for cookie in parsed_cookies:
            new = Cookie()
            new.update(cookie, url)

            for i in range(len(self.__cookies)):
                old = self.__cookies[i]

                if old.needs_update(new):
                    self.__cookies[i].update(cookie)
                    break
            else:
                self.__cookies.append(new)

    def set_domain(self, domain: str):
        self.__domain = domain

    def cookie_header(self, url: str):
        header_value = str()

        for cookie in self.__cookies:
            if cookie.match_url(url):
                header_value += cookie.name() + '=' + cookie.value() + '; '

        header_value = header_value.strip('; ')
        return header_value

    def get_all_as_dir(self):
        return [dict(cookie) for cookie in self.__cookies]

    def clear(self):
        self.__cookies.clear()
