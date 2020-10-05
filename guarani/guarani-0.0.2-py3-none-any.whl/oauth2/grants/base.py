from __future__ import annotations

from typing import Optional

from guarani.oauth2.adapter import BaseAdapter
from guarani.oauth2.configuration import Configuration
from guarani.oauth2.exceptions import InvalidScopeError
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2Request
from guarani.webtools import FullDict


class BaseGrant:
    """
    Base class responsible for defining the interface of an OAuth 2.1 Grant.

    The `Grant` is responsible for generating `Access Tokens` and, in some cases,
    `Authorization Grants` for Clients that need access to a protected resource
    of a web application (REST API, Web App, GraphQL, etc).

    Clients that want to access those protected resources **MUST** first obtain
    the consent of the `Resource Owner` for the desired resources. The resources
    can be accessed if the authorization contains the required `Scope` for it.

    Once the `Resource Owner` has granted the authorization to the `Client`,
    this one can then obtain an `Access Token` from the `Authorization Server`.

    This `Access Token` contains the scopes granted by the `Resource Owner` and
    allows the client to access the resources without further interaction
    with the `Resource Owner`.

    It is important to note that the scopes are defined on the application level,
    since they reflect its resources and the `Access Policies` of the application.

    :param request: Current request being processed.
    :type request: OAuth2Request

    :param adapter: Instance of the adapter used by the application.
    :type adapter: BaseAdapter

    :param config: Configuration of the provider.
    :type config: Configuration

    :cvar ``__authentication_methods__``: Allowed Client Authentication methods.
    :cvar ``__grant_type__``: Name of the Token Grant.
    :cvar ``__response_type__``: Name of the Authorization Grant.
    """

    __authentication_methods__: list[str] = None
    __grant_type__: str = None
    __response_type__: str = None

    def __init__(
        self,
        request: OAuth2Request,
        adapter: BaseAdapter,
        config: Configuration,
    ):
        self.request = request
        self.adapter = adapter
        self.config = config
        self.data = {}

    def create_token(
        self,
        access_token: str,
        expires_in: int,
        refresh_token: Optional[str] = None,
        scopes: Optional[list[str]] = None,
    ) -> dict:
        """
        Creates a `Token Response` with the following format::

            {
                "access_token": "2YotnFZFEjr1zCsicMWpAA",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token":"tGzv3JOkF0XG5Qx2TlKWIA",
                "scope": "scope1 scope2"
            }

        :param access_token: Access Token issued to the Client.
        :type access_token: str

        :param expires_in: Lifespan of the Access Token in seconds.
        :type expires_in: int

        :param refresh_token: Optional Refresh Token issued to the Client,
            defaults to None.
        :type refresh_token: str, optional

        :param scopes: Optional list of Scopes if the granted scopes are different
            than the scopes requested.
        :type scopes: list[str], optional

        :return: Bearer Token Response with the provided parameters.
        :rtype: dict
        """

        return FullDict(
            {
                "acces_token": access_token,
                "token_type": "Bearer",
                "expires_in": expires_in,
                "refresh_token": refresh_token,
                "scope": " ".join(scopes) if scopes else None,
            }
        )

    def validate_requested_scopes(
        self,
        scopes: list[str],
        client: ClientMixin,
        state: Optional[str] = None,
    ) -> None:
        """
        Verifies if all of the requested `Scopes`
        are supported by the `Authorization Server`.

        :param scopes: Requested scopes.
        :type scopes: list[str]

        :param client: Client that requested the provided scopes.
        :type client: ClientMixin

        :param state: State of the request provided by the Client, defaults to None.
        :type state: str, optional

        :raises InvalidScopeError: The Authorization Server does not support
            one or more of the requested scopes.
        """

        if scopes is None:
            return

        for scope in scopes:
            if scope not in self.config.scopes:
                raise InvalidScopeError(
                    description=f'Unsupported scope "{scope}".',
                    state=state,
                )

        if not set(scopes).issubset(set(client.get_allowed_scopes(scopes))):
            raise InvalidScopeError(
                description="This client is not authorized to request this scope.",
                state=state,
            )

    async def validate_authorization_request(self) -> None:
        """
        Validates the data provided by the `Client`
        in the `Authorization` portion of the `Grant`.
        """

        raise NotImplementedError

    async def create_authorization_response(self) -> str:
        """
        Creates the `Authorization Response` that will be returned to the `Client`.

        :return: URL to be redirect along with the response of the Grant.
        :rtype: str
        """

        raise NotImplementedError

    async def validate_token_request(self) -> None:
        """
        Validates the data provided by the `Client`
        in the `Token` portion of the `Grant`.
        """

        raise NotImplementedError

    async def create_token_response(self) -> dict:
        """
        Creates the `Token Response` that will be returned to the `Client`.

        :return: Dictionary containing the response from the Token Grant.
        :rtype: dict
        """

        raise NotImplementedError
