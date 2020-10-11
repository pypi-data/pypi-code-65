# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys
import inspect
from time import time
from hashlib import md5
import json

import requests

from zimupy.enums import ClientType, ResponseType, ErrorCode
from zimupy.exceptions import ZiMuZuException
from zimupy.client.api.base import BaseZiMuZuAPI


DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0)\
    Gecko/20100101 Firefox/32.0'

def _is_api_endpoint(obj):
    return isinstance(obj, BaseZiMuZuAPI)

class ZiMuZu(object):

        def __new__(cls, *args, **kwargs):
            self = super(ZiMuZu, cls).__new__(cls)
            if sys.version_info[:2] == (2, 6):
                # Python 2.6 inspect.gemembers bug workaround
                # http://bugs.python.org/issue1785
                for _class in cls.__mro__:
                    if issubclass(_class, ZiMuZu):
                        for name, api in _class.__dict__.items():
                            if isinstance(api, BaseZiMuZuAPI):
                                api_cls = type(api)
                                api = api_cls(self)
                                setattr(self, name, api)
            else:
                api_endpoints = inspect.getmembers(self, _is_api_endpoint)
                for name, api in api_endpoints:
                    api_cls = type(api)
                    api = api_cls(self)
                    setattr(self, name, api)
            return self

        def __init__(self,
                     access_key=None,
                     cid=None,
                     user_agent=DEFAULT_USER_AGENT,
                     proxy=None,
                     base_url='',
                     client=ClientType.iOS,
                     response_type=ResponseType.JSON):

            self.access_key = access_key
            self.cid = cid
            self.base_url = base_url
            self.client = client
            self.response_type = response_type
            self.g = 'api/v3'

            self.session = requests.Session()
            self.session.headers['User-Agent'] = user_agent

            self.request_body = {
                'g': 'api/v3',
                'a': '',
                'accesskey': '',
                'cid': self.cid,
                'timestamp': None,
                'client': self.client,
                'type': self.response_type,
            }

            if proxy:
                self.proxies = {'http': proxy}
                self.session.proxies = self.proxies

        def _gen_access_key(self, timestamp):
            raw_str = self.cid + '$$' + self.access_key + '&&' + str(timestamp)
            hash_str = md5(raw_str.encode('utf-8')).hexdigest()
            return hash_str

        def _request(self, method, url_or_endpoint, **kwargs):
            if not url_or_endpoint.startswith(('http://', 'https://')):
                api_base_url = kwargs.pop('api_base_url', self.base_url)
                url = '{base}{endpoint}'.format(
                    base=api_base_url,
                    endpoint=url_or_endpoint
                )
            else:
                url = url_or_endpoint

            ts = int(time())

            if isinstance(kwargs['params'], dict)\
                    and 'accesskey' not in kwargs['params']:
                kwargs['params']['accesskey'] = self.access_key
            if isinstance(kwargs['params'], dict)\
                    and 'timestamp' not in kwargs['params']:
                kwargs['params']['timestamp'] = ts
            if isinstance(kwargs['params'], dict)\
                    and 'cid' not in kwargs['params']:
                kwargs['params']['cid'] = self.cid
            if isinstance(kwargs['params'], dict)\
                    and 'client' not in kwargs['params']:
                kwargs['params']['client'] = self.client
            if isinstance(kwargs['params'], dict)\
                    and 'type' not in kwargs['params']:
                kwargs['params']['type'] = self.response_type
            if isinstance(kwargs['params'], dict)\
                    and 'g' not in kwargs['params']:
                kwargs['params']['g'] = self.g

            rsp = self.session.request(
                method=method,
                url=url,
                **kwargs
            )

            try:
                rsp.raise_for_status()
            except requests.RequestException:
                raise ZiMuZuException(code=None, message=None)

            if not isinstance(rsp, dict):
                ret = json.loads(rsp.content.decode('utf-8'))
            else:
                ret = rsp

            if 'status' in ret and ret['status'] != 0:
                code = ret['status']
                message = ret['info']
                if code and message != '':
                    raise ZiMuZuException(code, message)

            return ret['data']

        def get(self, url, **kwargs):
            return self._request(
                method='get',
                url_or_endpoint=url,
                **kwargs
            )

        _get = get

        def post(self, url, **kwargs):
            return self._request(
                method='post',
                url_or_endpoint=url,
                **kwargs
            )

        _post = post


