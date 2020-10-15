# -*- coding: utf-8 -*-
__author__ = 'jasonxu'


class BaseApiException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class AuthErrorException(BaseApiException):
    def __init__(self, message):
        BaseApiException.__init__(self, message)


class HttpErrorException(BaseApiException):
    def __init__(self, message):
        BaseApiException.__init__(self, message)
