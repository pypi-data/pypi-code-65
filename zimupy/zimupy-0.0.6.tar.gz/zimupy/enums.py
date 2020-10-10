# -*- coding: utf-8 -*-


class ClientType(object):
    iOS = 1
    Android = 2
    WindowsPhone = 3


class ResponseType(object):
    JSON = 'json'
    JSONP = 'jsonp'
    XML = 'xml'


class ErrorCode(object):
    InvalidParameter = 1001
    ParameterCheckFailed = 1002
    AccessKeyError = 1003
    InterfaceUnauthorized = 1004
    ParameterCheckFailed2 = 1011
    RequestTimeout = 1012
    NotLogin = 1021
