# -*- coding: utf-8 -*-
# Copyright (c) 2016 - 2020 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" AWS Lambda Adapter
"""
import base64
import logging
import sys

from ....exceptions import SqreenException
from ....frameworks.base import BaseRequest, BaseResponse
from ....rules import RuleCallback
from ....rules_callbacks.record_request_context import RecordRequestContext
from ....rules_callbacks.sqreen_error_page import BaseSqreenErrorPage

LOGGER = logging.getLogger(__name__)


class UnsupportedAWSLambdaEvent(SqreenException):

    def __init__(self, event):
        self.event = event

    def exception_infos(self):
        return {
            "event": self.event
        }


class AWSLambdaProxyV2Request(BaseRequest):
    """
    AWS Lambda Proxy Integration v2 event.
    """

    def __init__(self, event, storage=None):
        super(AWSLambdaProxyV2Request, self).__init__(storage=storage)
        self.event = event
        self.rc = event.get("requestContext")

    @property
    def remote_addr(self):
        return self.rc.get("http", {}).get("sourceIp")

    @property
    def hostname(self):
        return self.rc.get("domainName")

    @property
    def method(self):
        return self.event.get("httpMethod")

    @property
    def referer(self):
        return self.get_raw_header("referer")

    @property
    def client_user_agent(self):
        return self.rc.get("http", {}).get("userAgent")

    @property
    def path(self):
        return self.rc.get("path")

    @property
    def request_uri(self):
        return "?".join((self.event.get("rawPath"), self.event.get("rawQueryString")))

    @property
    def scheme(self):
        return self.event.get("headers", {}).get("x-forwarded-proto", "http")

    @property
    def server_port(self):
        return self.event.get("headers", {}).get("x-forwarded-port", "http")

    @property
    def remote_port(self):
        return None

    @property
    def view_params(self):
        return self.event.get("pathParameters")

    @property
    def body(self):
        isBase64Encoded = self.event.get("isBase64Encoded")
        body = self.event.get("body")
        if isBase64Encoded and body:
            return base64.b64decode(body)
        return body

    @property
    def form_params(self):
        # TODO
        return None

    @property
    def query_params(self):
        return self.event.get("queryStringParameters")

    @property
    def cookies_params(self):
        return self.event.get("cookies")

    @property
    def raw_headers(self):
        return self.event.get("headers")


class AWSLambdaProxyV1Request(BaseRequest):
    """
    AWS Lambda Proxy Integration event.
    """

    def __init__(self, event, storage=None):
        super(AWSLambdaProxyV1Request, self).__init__(storage=storage)
        self.event = event
        self.rc = event.get("requestContext")

    @property
    def remote_addr(self):
        return self.rc.get("identity", {}).get("sourceIp")

    @property
    def hostname(self):
        return self.rc.get("domainName")

    @property
    def method(self):
        return self.event.get("httpMethod")

    @property
    def referer(self):
        return self.get_raw_header("referer")

    @property
    def client_user_agent(self):
        return self.rc.get("identity", {}).get("userAgent")

    @property
    def path(self):
        return self.event.get("path")

    @property
    def scheme(self):
        return self.event.get("headers", {}).get("X-Forwarded-Proto", "http")

    @property
    def server_port(self):
        return self.event.get("headers", {}).get("X-Forwarded-Port")

    @property
    def remote_port(self):
        # No remote port in the event
        return None

    @property
    def view_params(self):
        return self.event.get("pathParameters")

    @property
    def body(self):
        isBase64Encoded = self.event.get("isBase64Encoded")
        body = self.event.get("body")
        if isBase64Encoded and body:
            return base64.b64decode(body)
        return body

    @property
    def form_params(self):
        # TODO
        return None

    @property
    def query_params(self):
        return self.event.get("queryStringParameters")

    @property
    def cookies_params(self):
        return None

    @property
    def raw_headers(self):
        # TODO header case
        return self.event.get("headers")


class AWSLambdaProxyV1Response(BaseResponse):

    def __init__(self, response):
        self.res = response

    @property
    def status_code(self):
        return self.res.get("statusCode")

    @property
    def content_type(self):
        # TODO header case
        return self.res.get("headers", {}).get("Content-Type")

    @property
    def content_length(self):
        # TODO header case
        cl = self.res.get("headers", {}).get("Content-Length")
        if cl is not None:
            try:
                return int(cl)
            except Exception:
                pass
        return None


class RecordRequestContextAWSLambda(RecordRequestContext):

    def pre(self, instance, args, kwars, **options):
        event = args[0]
        version = event.get("version")
        if version == "2.0":
            self._store_request(AWSLambdaProxyV2Request(event))
        elif version is None and "multiValueHeaders" in event:
            self._store_request(AWSLambdaProxyV1Request(event))
        else:
            raise UnsupportedAWSLambdaEvent(event)


class RecordResponseAWSLambda(RuleCallback):

    INTERRUPTIBLE = False

    def _record_response(self, options):
        result = options.get("result")
        if result:
            response = AWSLambdaProxyV1Response(result)
            self.storage.store_response(response)

    def post(self, instance, args, kwargs, **options):
        self._record_response(options)

    def failing(self, instance, args, kwargs, **options):
        self._record_response(options)


class SqreenErrorPageAWSLambda(BaseSqreenErrorPage):

    def failing(self, instance, args, kwargs, exc_info=None, **options):
        ret = self.handle_exception(exc_info[1])
        if ret is not None:
            status_code, body, headers = ret
            return {
                "status": "override",
                "new_return_value": {
                    "statusCode": status_code,
                    "headers": headers,
                    "isBase64Encoded": False,
                    "body": body,
                }
            }


class FlushLogs(RuleCallback):

    INTERRUPTIBLE = False

    def post(self, instance, args, kwars, **options):
        self._flush()

    def failing(self, instance, args, kwars, **options):
        self._flush()

    def _flush(self):
        self.runner.aggregate_observations()
        self.runner.publish_metrics()
        # Drain deliverer
        self.runner.deliverer.drain(resiliently=False)


class AWSLambdaFrameworkAdapter:

    def instrumentation_callbacks(self, runner, storage):
        # The module must be similar to the strategy MODULE_NAME
        module = "__main__" if sys.version_info[:2] != (3, 7) else "bootstrap"
        return [
            RecordRequestContextAWSLambda.from_rule_dict({
                "name": "ecosystem_aws_lambda_request_context",
                "rulespack_id": "ecosystem/transport",
                "block": False,
                "test": False,
                "hookpoint": {
                    "klass": "{}::None".format(module),
                    "method": "handle_event_request",
                    "strategy": "aws_lambda",
                },
                "callbacks": {},
                "priority": 20,
            }, runner, storage),
            RecordResponseAWSLambda.from_rule_dict({
                "name": "ecosystem_aws_lambda_record_response",
                "rulespack_id": "ecosystem/transport",
                "block": False,
                "test": False,
                "hookpoint": {
                    "klass": "{}::None".format(module),
                    "method": "handle_event_request",
                    "strategy": "aws_lambda",
                },
                "priority": 30,
            }, runner, storage),
            SqreenErrorPageAWSLambda.from_rule_dict({
                "name": "ecosystem_aws_lambda_error_page",
                "rulespack_id": "ecosystem/transport",
                "block": True,
                "test": False,
                "hookpoint": {
                    "klass": "{}::None".format(module),
                    "method": "handle_event_request",
                    "strategy": "aws_lambda",
                },
                "priority": 100,
            }, runner, storage),
            FlushLogs.from_rule_dict({
                "name": "ecosystem_aws_lambda_flush_logs",
                "rulespack_id": "ecosystem/transport",
                "block": False,
                "test": False,
                "hookpoint": {
                    "klass": "{}::None".format(module),
                    "method": "handle_event_request",
                    "strategy": "aws_lambda",
                },
                "callbacks": {},
                "priority": 10,
            }, runner, storage),
        ]
