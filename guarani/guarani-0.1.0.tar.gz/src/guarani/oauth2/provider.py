from __future__ import annotations

from typing import Any, Type

from guarani.oauth2.adapter import BaseAdapter
from guarani.oauth2.authentication import BaseClientAuthentication
from guarani.oauth2.configuration import Configuration
from guarani.oauth2.endpoints import AuthorizationEndpoint, BaseEndpoint, TokenEndpoint
from guarani.oauth2.exceptions import InvalidClient
from guarani.oauth2.grants import BaseGrant
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2Request, OAuth2Response


class Provider:
    """
    Base class of the `Authorization Server` integration.

    The abstract methods of this class **MUST** be implemented by integrations
    of async web frameworks.

    :param issuer: Base URL of the Authorization Server.
    :type issuer: str

    :param adapter: Implementation of the common functionalities of the Provider.
    :type adapter: type[BaseAdapter]

    :param grants: List of the Grants supported by the Authorization Server.
    :type grants: list[type[BaseGrant]]

    :param auth_methods: Authentication methods to authenticate the Client.
    :type auth_methods: list[type[BaseClientAuthentication]]

    :param scopes: List of the Scopes supported by the Authorization Server.
    :type scopes: list[str]

    :param error_url: URL of the error page of the Authorization Server
        for Fatal Errors regarding the Authorization Endpoint.
    :type error_url: str

    :param token_lifespan: Lifespan of the Access Token in seconds, defaults to 3600.
    :type token_lifespan: int, optional
    """

    def __init__(
        self,
        issuer: str,
        *,
        adapter: Type[BaseAdapter],
        grants: list[Type[BaseGrant]],
        auth_methods: list[Type[BaseClientAuthentication]],
        scopes: list[str],
        error_url: str,
        token_endpoint: str,
        token_lifespan: int = 3600,
    ):
        self.adapter = adapter()
        self.config = Configuration(
            issuer=issuer,
            grants=grants,
            scopes=scopes,
            error_url=error_url,
            token_endpoint=token_endpoint,
            token_lifespan=token_lifespan,
        )

        self.auth_methods = [
            method(self.adapter.find_client, self.config) for method in auth_methods
        ]

        self.endpoints = {}

    def register_endpoint(self, endpoint: Type[BaseEndpoint]):
        """
        Registers a new endpoint within the Provider.

        The endpoint **MUST** be a subclass of :class:`BaseEndpoint`.

        To run the endpoint against the current request, simply call
        the method :meth:`endpoint` with the name of the endpoint
        and the current request.

        :param endpoint: Endpoint to be registered in the Provider.
        :type endpoint: type[BaseEndpoint]
        """

        self.endpoints[endpoint.__endpoint__] = endpoint

    async def authenticate(
        self, request: OAuth2Request, methods: list[str] = None
    ) -> ClientMixin:
        """
        Gets the client from the application's storage and validates its data.

        :param request: Current request being handled.
        :type request: OAuth2Request

        :param methods: Methods allowed by the endpoint, defaults to None.
            If no value is provided, it tests against all registered methods.
        :type methods: list[str], optional

        :raises InvalidClient: The requested client is invalid.

        :return: Authenticated Client.
        :rtype: ClientMixin
        """

        for method in self.auth_methods:
            if methods and method.__method__ not in methods:
                continue

            client = await method.authenticate(request)

            if not client:
                continue

            request.client = client
            return client

        raise InvalidClient

    async def authorize(self, request: Any) -> Any:
        """
        Handles requests to the `Authorization Endpoint`.

        :param request: Current request of the integrated web framework.
        :type request: Any

        :return: Authorization Response in the format specified
            by the integrated web framework.
        :rtype: Any
        """

        request = await self.create_request(request)
        endpoint = AuthorizationEndpoint(self.adapter, self.config, self.authenticate)
        response = await endpoint(request)
        return await self.create_response(response)

    async def token(self, request: Any) -> Any:
        """
        Handles requests to the `Token Endpoint`.

        :param request: Current request of the integrated web framework.
        :type request: Any

        :return: Token Response in the format specified by the integrated web framework.
        :rtype: Any
        """

        request = await self.create_request(request)
        endpoint = TokenEndpoint(self.adapter, self.config, self.authenticate)
        response = await endpoint(request)
        return await self.create_response(response)

    async def endpoint(self, name: str, request: Any) -> Any:
        """
        Executes the flow of the chosen extension endpoint against the current request.

        In order to run the endpoint, it **MUST** first be registered in the Provider
        via the method :meth:`register_endpoint`.

        :param name: Name of the registered endpoint to be executed.
        :type name: str

        :param request: Current request of the integrated web framework.
        :type request: Any

        :return: Extension endpoint response in the format specified
            by the integrated web framework.
        :rtype: Any
        """

        endpoint_cls: Type[BaseEndpoint] = self.endpoints.get(name)

        if endpoint_cls is None:
            raise RuntimeError(f'The endpoint "{name}" is not registered.')

        request = await self.create_request(request)
        endpoint = endpoint_cls(self.adapter, self.config, self.authenticate)
        response = await endpoint(request)
        return await self.create_response(response)

    async def create_request(self, request: Any) -> OAuth2Request:
        """
        Transforms the Web Server's request into an OAuth2Request object.

        This method **MUST** be implemented in integrations.

        :param request: Web Server's specific request object.
        :type request: Any

        :return: Transformed request object.
        :rtype: OAuth2Request
        """

        raise NotImplementedError

    async def create_response(self, response: OAuth2Response) -> Any:
        """
        Transforms the `OAuth2Response` object into a Response of the integrated Web Server.

        This method **MUST** be implemented in integrations.

        :param response: Framework's Response.
        :type response: OAuth2Response

        :return: Integrated Web Server Response.
        :rtype: Any
        """

        raise NotImplementedError
