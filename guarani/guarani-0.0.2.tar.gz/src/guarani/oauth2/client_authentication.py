from __future__ import annotations

from typing import Awaitable, Callable

from guarani.oauth2.exceptions import InvalidClientError
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2Request
from guarani.webtools import get_basic_authorization


class ClientAuthentication:
    def __init__(self, find_client: Callable[[str], Awaitable[ClientMixin]]):
        self.find_client = find_client
        self._methods = {
            "client_secret_basic": client_secret_basic,
            "client_secret_post": client_secret_post,
            "none": none,
        }
        self._error_headers = {"client_secret_basic": {"WWW-Authenticate": "Basic"}}

    async def __call__(
        self,
        request: OAuth2Request,
        methods: list[str] = None,
    ) -> ClientMixin:
        return await self.authenticate_client(request, methods)

    def include_auth_method(
        self,
        method: str,
        func: Callable[[OAuth2Request], tuple[str, str]],
    ):
        """
        Registers a new `Client Authentication Method`.

        :param method: Name of the authentication method.
        :type method: str

        :param func: Function that extracts the Client's Credentials from the Request.
        :type func: Callable[[OAuth2Request], tuple[str, str]]
        """

        self._methods[method] = func

    async def authenticate_client(
        self,
        request: OAuth2Request,
        methods: list[str] = None,
    ) -> ClientMixin:
        """
        Gets the client from the application's storage and validates its data.

        :param request: Current request being handled.
        :type request: OAuth2Request

        :param methods: Methods allowed by the endpoint, defaults to None.
            If no value is provided, it tests against all registered methods.
        :type methods: list[str], optional

        :raises InvalidClientError: The requested client is invalid.

        :return: Authenticated Client.
        :rtype: ClientMixin
        """

        for method, func in self._methods.items():
            if methods and method not in methods:
                continue

            client_id, client_secret = func(request)

            if not client_id:
                continue

            client = await self.find_client(client_id)

            headers = self._error_headers.get(method, {})

            if not client:
                raise InvalidClientError(
                    description="Client not found.",
                    headers=headers,
                )

            if not client.validate_client_secret(client_secret):
                raise InvalidClientError(
                    description="Mismatching Client Secret.",
                    headers=headers,
                )

            if not client.validate_token_endpoint_auth_method(method):
                raise InvalidClientError(
                    description=f'Client is not allowed to use the method "{method}".',
                    headers=headers,
                )

            request.client = client
            return client

        raise InvalidClientError


def client_secret_basic(request: OAuth2Request) -> tuple[str, str]:
    """
    Implements the Client Authentication via the Basic Authentication workflow.

    If this workflow is enabled, it will look at the Authorization header
    for a scheme similar to the following::

        Basic Y2xpZW50MTpjbGllbnQxc2VjcmV0

    This scheme denotes the type of the flow, which in this case is `Basic`,
    and the Client Credentials, that is a Base64 encoded string that contains
    the Credentials in the format `client_id:client_secret`.
    """

    return get_basic_authorization(request.headers)


def client_secret_post(request: OAuth2Request) -> tuple[str, str]:
    """
    Implements the client authentication via the Body Post workflow.

    If this workflow is enabled, it will look at the Body of the request
    for a scheme similar to the following::

        client_id=client1&client_secret=client1secret

    The request's body often comes with more information that may pertain to
    a specific endpoint or authorization grant. In this case,
    the body will be similar to the following::

        key1=value1&key2=value2&client_id=client1&client_secret=client1secret

    This scheme contains the Client's ID and Secret issued upon creation.
    The usage of this scheme is **NOT RECOMMENDED** unless the client
    is unable to use another scheme.
    """

    body = request.form()

    client_id, client_secret = body.get("client_id"), body.get("client_secret")

    if not client_id or not client_secret:
        return None, None

    return client_id, client_secret


def none(request: OAuth2Request) -> tuple[str, str]:
    """
    Implements the client authentication via the body of the request.

    If this workflow is enabled, it will look at the body of the request
    for a scheme similar to the following::

        client_id=client1

    The request's body often comes with more information that may pertain to
    a specific endpoint or authorization grant. In this case,
    the body will be similar to the following::

        key1=value1&key2=value2&client_id=client1

    In this workflow, if the client provides a client_secret,
    it will automatically fail, since it is intended to be used by public clients.
    """

    body = request.form()

    client_id, client_secret = body.get("client_id"), body.get("client_secret")

    if not client_id or client_secret:
        return None, None

    return client_id, client_secret
