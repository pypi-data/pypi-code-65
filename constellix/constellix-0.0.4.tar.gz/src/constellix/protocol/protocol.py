# -*- coding: utf-8 -*-
"""
Protocol handler for Constellix
"""

import asyncio
import backoff
import base64
import functools
import hashlib
import hmac
import logging
import os
import requests
import sys
import time

from ..exceptions import ConstellixAPIError

_LOGGER = logging.getLogger(__name__)
logging.getLogger("backoff").addHandler(logging.StreamHandler())

_DEFAULT_HOST = "api.dns.constellix.com"
_DEFAULT_VERSION = 1

_REFRENCE = "https://github.com/aperim/python-constellix"
"""Used to identify this to Constellix API"""

_USER_AGENT = f"Mozilla/5.0 (compatible; Aperim; +{_REFRENCE})"
"""The User Agent for Constellix API calls"""


def fatal_code(e):
    if e.response.status_code == 401:
        return False
    return 400 <= e.response.status_code < 500


class Protocol(object):
    def __init__(
        self, api_key=None, secret_key=None, host=None, version=None, loop=None
    ):
        super().__init__()
        self.__loop = loop if loop else asyncio.get_event_loop()
        self.__api_key = api_key if api_key else None
        self.__secret_key = secret_key if secret_key else None
        self.__host = host if host else _DEFAULT_HOST
        self.__version = version if host else _DEFAULT_VERSION

        self.__api_url = f"https://{self.__host}/v{self.__version}"

        self.__session = None

    async def api_get(self, path=None, params=None, headers=None):
        """Make a GET request to the Constellix API

        Attributes:
            path (str): The path to the endpoint
            params (str): Any URL paramaters to pass
            headers (dict): Headers to be sent in the request
        """

        if path:
            if not path.startswith("/"):
                path = f"/{path}"
        else:
            path = ""

        url = f"{self.__api_url}{path}"
        return await self.__loop.run_in_executor(
            None, self.__request, "GET", url, params, None, headers
        )

    async def api_post(self, path=None, params=None, json=None, headers=None):
        """Make a POST request to the Constellix API

        Attributes:
            path (str): The path to the endpoint
            params (str): Any URL paramaters to pass
            json (str): JSON to be passed in the body
            headers (dict): Headers to be sent in the request
        """

        if path:
            if not path.startswith("/"):
                path = f"/{path}"
        else:
            path = ""

        url = f"{self.__api_url}{path}"
        return await self.__loop.run_in_executor(
            None, self.__request, "POST", url, params, json, headers
        )

    async def api_put(self, path=None, params=None, json=None, headers=None):
        """Make a PUT request to the Constellix API

        Attributes:
            path (str): The path to the endpoint
            params (str): Any URL paramaters to pass
            json (str): JSON to be passed in the body
            headers (dict): Headers to be sent in the request
        """

        if path:
            if not path.startswith("/"):
                path = f"/{path}"
        else:
            path = ""

        url = f"{self.__api_url}{path}"
        return await self.__loop.run_in_executor(
            None, self.__request, "PUT", url, params, json, headers
        )

    async def api_delete(self, path=None, params=None, json=None, headers=None):
        """Make a DELETE request to the Constellix API

        Attributes:
            path (str): The path to the endpoint
            params (str): Any URL paramaters to pass
            json (str): JSON to be passed in the body
            headers (dict): Headers to be sent in the request
        """

        if path:
            if not path.startswith("/"):
                path = f"/{path}"
        else:
            path = ""

        url = f"{self.__api_url}{path}"
        return await self.__loop.run_in_executor(
            None, self.__request, "DELETE", url, params, json, headers
        )

    def __get_session(self):
        if self.__session:
            return self.__session
        self.__session = requests.session()
        self.__session.headers = {
            "User-Agent": _USER_AGENT,
            "Referer": _REFRENCE,
            "Content-Type": "application/json",
        }
        return self.__session

    @backoff.on_exception(
        backoff.fibo,
        ConstellixAPIError,
        max_time=300,
        giveup=fatal_code,
    )
    def __request(self, method="GET", url=None, params=None, json=None, headers=None):

        _LOGGER.debug(
            {
                "url": url,
                "params": params,
                "data": json,
                "headers": headers,
            }
        )

        session = self.__get_session()

        if not headers:
            headers = {}

        headers["x-cns-security-token"] = self.token

        try:
            response = session.request(
                method, url, params=params, json=json, headers=headers
            )
        except Exception as err:
            raise ConstellixAPIError(
                message="Unkown error from Constellix API", exception=err
            )

        status_code = getattr(response, "status_code", None)

        try:
            data = response.json()
        except:
            data = None

        if not status_code:
            raise ConstellixAPIError(
                message="Constellix API failed to repond.", response=response
            )

        success = 200 <= response.status_code <= 299

        if response.status_code == 401 or response.status_code == 403:
            raise ConstellixAPIError(
                message="Constellix API Access Denied",
                response=response,
            )

        if not success:
            raise ConstellixAPIError(
                message="Constellix API Error",
                response=response,
            )

        return data

    @property
    def token(self):
        key = bytes(self.__secret_key, "UTF-8")
        epoch_ms = str(round(time.time_ns() / 1000000))
        message = bytes(epoch_ms, "UTF-8")

        digester = hmac.new(key, message, hashlib.sha1)
        signature1 = digester.digest()
        signature2 = base64.urlsafe_b64encode(signature1)
        hmacdata = str(signature2, "UTF-8")

        return f"{self.__api_key}:{hmacdata}:{epoch_ms}"
