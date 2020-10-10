from __future__ import annotations

from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from guarani.oauth2.grants import BaseGrant


class Configuration:
    """
    Class that holds the configuration of the Provider.

    These configurations are used throughout the package and are essential
    for the dynamicity of the Framework. The configuration parameters are
    supplied when instantiating a Provider for the application.

    :param issuer: Base URL of the application.
    :type issuer: str

    :param grants: List of the Grants that will be supported by the application.
    :type grants: list[type[BaseGrant]]

    :param scopes: List of the scopes that will be supported by the application.
    :type scopes: list[str]

    :param error_url: URL of the error page of the Authorization Server.
        Used to display a fatal error to the User when granting authorization.
    :type error_url: str

    :param token_lifespan: Lifespan of the Access Token issued by the Provider.
    :type token_lifespan: int

    :ivar issuer: Base URL of the application.
    :ivar authorization_grants: List of the Grants that have an Authorization workflow.
    :ivar token_grants: List of the Grants that have a Token workflow.
    :ivar scopes: List of the scopes that will be supported by the application.
    :ivar error_url: URL of the error page of the Authorization Server.
        Used to display a fatal error to the User when granting authorization.
    :ivar token_lifespan: Lifespan of the Access Token issued by the Provider.
    """

    def __init__(
        self,
        issuer: str,
        grants: list[Type[BaseGrant]],
        scopes: list[str],
        error_url: str,
        token_endpoint: str,
        token_lifespan: int,
    ):
        self.issuer = issuer
        self.authorization_grants = [
            grant for grant in grants if grant.__response_type__ is not None
        ]
        self.token_grants = [
            grant for grant in grants if grant.__grant_type__ is not None
        ]
        self.scopes = scopes
        self.error_url = error_url
        self.token_endpoint = token_endpoint
        self.token_lifespan = token_lifespan
