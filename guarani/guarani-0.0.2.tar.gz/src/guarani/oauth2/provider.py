from __future__ import annotations

from typing import Any, Type

from guarani.oauth2.adapter import BaseAdapter
from guarani.oauth2.client_authentication import ClientAuthentication
from guarani.oauth2.configuration import Configuration
from guarani.oauth2.endpoints.authorization import AuthorizationEndpoint
from guarani.oauth2.endpoints.base import BaseEndpoint
from guarani.oauth2.endpoints.token import TokenEndpoint
from guarani.oauth2.grants.base import BaseGrant
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
        scopes: list[str],
        error_url: str,
        token_lifespan: int = 3600,
    ):
        self.adapter = adapter()
        self.config = Configuration(
            issuer=issuer,
            grants=grants,
            scopes=scopes,
            error_url=error_url,
            token_lifespan=token_lifespan,
        )
        self.client_auth = ClientAuthentication(self.adapter.find_client)

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
        endpoint = AuthorizationEndpoint(
            request,
            self.adapter,
            self.config,
            self.client_auth,
        )
        response = await endpoint()
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
        endpoint = TokenEndpoint(request, self.adapter, self.config, self.client_auth)
        response = await endpoint()
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
        endpoint = endpoint_cls(request, self.adapter, self.config, self.client_auth)
        response = await endpoint()
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
