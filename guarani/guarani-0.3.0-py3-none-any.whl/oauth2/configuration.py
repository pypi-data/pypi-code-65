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
        authorization_endpoint: str,
        token_endpoint: str,
        jwks_uri: str,
        registration_endpoint: str,
        token_lifespan: int,
        token_endpoint_auth_methods: list[str],
        token_endpoint_signing_algs: list[str],
        service_documentation: str,
        ui_locales_supported: list[str],
        op_policy_uri: str,
        op_tos_uri: str,
        revocation_endpoint: str,
        revocation_endpoint_auth_methods: list[str],
        revocation_endpoint_signing_algs: list[str],
        introspection_endpoint: str,
        introspection_endpoint_auth_methods: list[str],
        introspection_endpoint_signing_methods: list[str],
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
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.jwks_uri = jwks_uri
        self.registration_endpoint = registration_endpoint
        self.token_lifespan = token_lifespan
        self.token_endpoint_auth_methods = token_endpoint_auth_methods
        self.token_endpoint_signing_algs = token_endpoint_signing_algs
        self.service_documentation = service_documentation
        self.ui_locales_supported = ui_locales_supported
        self.op_policy_uri = op_policy_uri
        self.op_tos_uri = op_tos_uri
        self.revocation_endpoint = revocation_endpoint
        self.revocation_endpoint_auth_methods = revocation_endpoint_auth_methods
        self.revocation_endpoint_signing_algs = revocation_endpoint_signing_algs
        self.introspection_endpoint = introspection_endpoint
        self.introspection_endpoint_auth_methods = introspection_endpoint_auth_methods
        self.introspection_endpoint_signing_methods = (
            introspection_endpoint_signing_methods
        )
