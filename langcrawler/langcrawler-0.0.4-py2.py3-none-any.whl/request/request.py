# -*- coding: utf-8 -*-

import json
import requests

from requests.adapters import HTTPAdapter


class RequestException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Request(object):
    def __init__(self, retry=1, timeout=None):
        if retry < 0:
            raise RequestException("retry invalid: %d" % retry)

        if isinstance(timeout, int) and timeout < 0:
            raise RequestException("timeout invalid: %d" % timeout)

        self._retry = retry
        self._timeout = timeout

    def run(self, url):
        session = requests.Session()
        session.keep_alive = False
        session.mount("https://", HTTPAdapter(max_retries=self._retry))
        response = session.get(url=url, timeout=self._timeout)
        session.close()

        if response.status_code != requests.codes.ok:
            raise RequestException("failed to run: %s" % url)

        return json.loads(response.text.replace(")]}'", ""))
