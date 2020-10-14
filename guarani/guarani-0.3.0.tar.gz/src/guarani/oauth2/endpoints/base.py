from __future__ import annotations

from typing import Awaitable, Callable

from guarani.oauth2.adapter import BaseAdapter
from guarani.oauth2.configuration import Configuration
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2Request, OAuth2Response


class BaseEndpoint:
    """
    Base class for the endpoints of the OAuth 2.1 framework and its extensions.

    Any endpoint being implemented by the application or by extensions **MUST**
    inherit from this class and implement its abstract methods.

    The type, status, headers and body of the response it returns,
    as well as its meaning and formatting have to be documented
    by the respective endpoint.

    The method :meth:`create_response` **MUST NOT** raise exceptions.
    It **MUST** catch the exceptions and return a valid error response instead.

    :cvar ``__endpoint__``: Name of the endpoint.

    :param adapter: Adapter registered within the Provider.
    :type adapter: BaseAdapter

    :param config: Configuration data of the Provider.
    :type config: Configuration

    :param authenticate: Method of the Provider to authenticate the Client.
    :type authenticate: Callable[[OAuth2Request, list[str]], Awaitable[ClientMixin]]
    """

    __endpoint__: str = None

    def __init__(
        self,
        adapter: BaseAdapter,
        config: Configuration,
        authenticate: Callable[[OAuth2Request, list[str]], Awaitable[ClientMixin]],
    ) -> None:
        self.adapter = adapter
        self.config = config
        self.authenticate = authenticate

    async def __call__(self, request: OAuth2Request) -> OAuth2Response:
        """
        All endpoints are required to implement this method,
        since it MUST return a response back to the client.

        The type, status, headers and body of the response it returns,
        as well as its meaning and formatting have to be documented by
        the respective endpoint.

        This method **MUST NOT** raise **ANY** exception.

        If an error occurred during the processing of the request,
        it **MUST** be treated and its appropriate response status,
        headers and body **MUST** be correctly set
        to denote the type of exception that occured.

        Other than the previous requirements, the endpoint is free
        to use whatever tools, methods and workflows it wished.

        It is recommended to split the logic of the endpoint into small
        single-responsibility methods for better maintenance.

        :param request: Current request being processed.
        :type request: OAuth2Request

        :return: Response containing all the necessary info to the client.
        :rtype: OAuth2Response
        """

        raise NotImplementedError
