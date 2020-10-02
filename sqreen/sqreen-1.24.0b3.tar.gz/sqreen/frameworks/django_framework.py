# -*- coding: utf-8 -*-
# Copyright (c) 2016 - 2020 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Django specific WSGI HTTP Request / Response stuff
"""
from copy import deepcopy
from logging import getLogger

import pkg_resources

from ..utils import cached_property, to_unicode_safe
from .base import BaseResponse
from .wsgi import BaseWSGIRequest

LOGGER = getLogger(__name__)


def drf_preload_data():
    """Detect if request data should be preloaded for Django Rest Framework.

    See https://github.com/encode/django-rest-framework/issues/3951.
    """
    for package in pkg_resources.working_set:
        if package.project_name == "djangorestframework":
            drf_version_info = tuple(map(int, package.version.split(".")[:2]))
            return (3, 3) <= drf_version_info <= (3, 4)
    return False


class DjangoRequest(BaseWSGIRequest):

    DRF_PRELOAD_DATA = drf_preload_data()

    def __init__(self, request, storage=None):
        super(DjangoRequest, self).__init__(storage=storage)
        self.request = request

    @cached_property
    def query_params(self):
        try:
            # Convert django QueryDict to a normal dict with values as list
            return dict(self.request.GET.lists())
        except Exception:
            LOGGER.debug("couldn't get request.GET from the framework",
                         exc_info=True)
            return super(DjangoRequest, self).query_params

    @property
    def body(self):
        try:
            return self.request.body
        except Exception:  # UnreadablePostError, RawPostDataException, RequestDataTooBig
            LOGGER.debug("couldn't get request.body from the framework",
                         exc_info=True)
            return super(DjangoRequest, self).body

    @cached_property
    def form_params(self):
        try:
            if (
                self.DRF_PRELOAD_DATA
                and self.request.method == "POST"
                and not getattr(self.request, "_read_started", False)
            ):
                self.request.body
            return deepcopy(self.request.POST)
        except Exception:
            # Django can raise ValueError or TypeError exceptions when
            # parsing the HTTP body for reading POST data.
            LOGGER.debug("couldn't get request.POST from framework",
                         exc_info=True)
            return super(DjangoRequest, self).form_params

    @cached_property
    def cookies_params(self):
        try:
            return self.request.COOKIES
        except Exception:
            LOGGER.debug("couldn't get request.COOKIES from framework",
                         exc_info=True)
            return super(DjangoRequest, self).cookies_params

    @property
    def remote_addr(self):
        return to_unicode_safe(self.get_raw_header("REMOTE_ADDR"))

    @property
    def hostname(self):
        try:
            return self.request.get_host()
        except Exception:
            LOGGER.debug("couldn't get request.get_host from the framework",
                         exc_info=True)
            return None

    @property
    def method(self):
        return self.request.method

    @property
    def referer(self):
        return to_unicode_safe(self.get_raw_header("HTTP_REFERER"))

    @property
    def client_user_agent(self):
        return to_unicode_safe(self.get_raw_header("HTTP_USER_AGENT"))

    @property
    def route(self):
        """Request route."""
        # The resolver_match attribute is set only set once all request
        # middlewares have been called.
        resolver_match = getattr(self.request, "resolver_match", None)
        return getattr(resolver_match, "view_name", None)

    @property
    def path(self):
        return self.request.path

    @property
    def scheme(self):
        return getattr(self.request, "scheme", None)

    @property
    def server_port(self):
        return to_unicode_safe(self.get_raw_header("SERVER_PORT"))

    @property
    def remote_port(self):
        return to_unicode_safe(self.get_raw_header("REMOTE_PORT"))

    @property
    def raw_headers(self):
        return self.request.META

    @property
    def view_params(self):
        resolver_match = getattr(self.request, "resolver_match", None)
        if resolver_match:
            return resolver_match.kwargs


class DjangoResponse(BaseResponse):

    def __init__(self, response):
        self.response = response

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def content_type(self):
        return self.response.get("Content-Type")

    @property
    def content_length(self):
        try:
            return int(self.response.get("Content-Length"))
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
