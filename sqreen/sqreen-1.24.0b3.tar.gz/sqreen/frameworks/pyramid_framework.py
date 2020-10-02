# -*- coding: utf-8 -*-
# Copyright (c) 2016 - 2020 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Pyramid specific WSGI HTTP Request / Response stuff
"""
from copy import deepcopy
from logging import getLogger

from ..utils import cached_property, is_json_serializable
from .base import BaseResponse
from .wsgi import BaseWSGIRequest

LOGGER = getLogger(__name__)


class PyramidRequest(BaseWSGIRequest):

    def __init__(self, request, storage=None):
        super(PyramidRequest, self).__init__(storage=storage)
        self.request = request

    @cached_property
    def query_params(self):
        try:
            # Convert pyramid MultiDict to a normal dict with values as list
            return dict(self.request.GET.dict_of_lists())
        except Exception:
            LOGGER.debug("couldn't get request.GET from the framework",
                         exc_info=True)
            return super(PyramidRequest, self).query_params

    @property
    def body(self):
        try:
            return self.request.body
        except Exception:
            LOGGER.debug("couldn't get request.body from the framework",
                         exc_info=True)
            return super(PyramidRequest, self).body

    @cached_property
    def form_params(self):
        try:
            # Convert pyramid MultiDict to a normal dict with values as list
            form_params = {}
            post_params = self.request.POST
            for param_name in post_params:
                values = post_params.getall(param_name)
                # Ignore any non json serializable value as we don't know
                # how to process them (like cgi.FieldStorage)
                form_params[param_name] = list(
                    filter(is_json_serializable, values)
                )
            return form_params
        except Exception:
            LOGGER.debug("couldn't get request.POST from framework",
                         exc_info=True)
            return super(PyramidRequest, self).form_params

    @cached_property
    def cookies_params(self):
        try:
            return dict(self.request.cookies)
        except Exception:
            LOGGER.debug("couldn't get request.cookies from framework",
                         exc_info=True)
            return super(PyramidRequest, self).cookies_params

    @property
    def remote_addr(self):
        """Remote IP address."""
        return self.request.remote_addr

    @property
    def hostname(self):
        return self.request.host

    @property
    def method(self):
        return self.request.method

    @property
    def referer(self):
        return self.get_raw_header("HTTP_REFERER")

    @property
    def client_user_agent(self):
        return self.request.user_agent

    @property
    def route(self):
        """Request route."""
        route = getattr(self.request, "matched_route", None)
        pattern = getattr(route, "pattern", None)
        return pattern

    @property
    def path(self):
        return self.request.path

    @property
    def scheme(self):
        return self.request.scheme

    @property
    def server_port(self):
        return self.get_raw_header("SERVER_PORT")

    @property
    def remote_port(self):
        return self.get_raw_header("REMOTE_PORT")

    @property
    def view_params(self):
        return self.request.matchdict

    @cached_property
    def json_params(self):
        try:
            return deepcopy(self.request.json_body)
        except Exception:
            LOGGER.debug("couldn't get request.json_body from the framework",
                         exc_info=True)
            return super(PyramidRequest, self).json_params

    @property
    def raw_headers(self):
        return self.request.environ


class PyramidResponse(BaseResponse):

    def __init__(self, response):
        self.response = response

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def content_type(self):
        return self.response.headers.get("Content-Type")

    @property
    def content_length(self):
        try:
            return int(self.response.content_length)
        except (ValueError, TypeError):
            return None

    @property
    def headers_no_cookies(self):
        result = {}
        for header_name, value in self.response.items():
            name = header_name.lower().replace("_", "-")
            if name == "set-cookie":
                continue
            result[name] = value
        return result
