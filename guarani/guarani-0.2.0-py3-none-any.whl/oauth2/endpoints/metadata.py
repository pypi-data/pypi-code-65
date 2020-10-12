from __future__ import annotations

from urllib.parse import urljoin

from guarani.oauth2.endpoints.base import BaseEndpoint
from guarani.oauth2.models import OAuth2JSONResponse, OAuth2Request
from guarani.webtools import FullDict


class MetadataEndpoint(BaseEndpoint):
    """
    Endpoint used by the `Client` to obtain the metadata of the Authorization Server.

    This endpoint implements **ALL** the attributes defined by
    `RFC 8414 <https://tools.ietf.org/html/rfc8414>`_.

    The majority of the attributes supported by this endpoint has to be defined
    at the instantiation of the `Provider` by passing in the respective
    keyword arguments.

    .. note:: Some attributes of this endpoint are shortened in the instantiation
        of the Provider.
    """

    __endpoint__: str = "metadata"

    async def __call__(self, request: OAuth2Request) -> OAuth2JSONResponse:
        metadata = self.resolve_metadata()
        return OAuth2JSONResponse(body=metadata)

    def resolve_metadata(self) -> dict:
        """
        Helper method used to resolve the dictionary that will be used
        as the body of the Response of this Endpoint.

        :return: Resolved metadata of the Provider.
        :rtype: dict
        """

        issuer = self.config.issuer
        authorization_endpoint = urljoin(issuer, self.config.authorization_endpoint)
        token_endpoint = urljoin(issuer, self.config.token_endpoint)
        registration_endpoint = (
            urljoin(issuer, self.config.registration_endpoint)
            if self.config.registration_endpoint
            else None
        )
        revocation_endpoint = (
            urljoin(issuer, self.config.revocation_endpoint)
            if self.config.revocation_endpoint
            else None
        )
        introspection_endpoint = (
            urljoin(issuer, self.config.introspection_endpoint)
            if self.config.introspection_endpoint
            else None
        )
        jwks_uri = (
            urljoin(issuer, self.config.jwks_uri) if self.config.jwks_uri else None
        )
        response_types = [
            grant.__response_type__ for grant in self.config.authorization_grants
        ]
        grant_types = [grant.__grant_type__ for grant in self.config.token_grants]

        return FullDict(
            issuer=issuer,
            authorization_endpoint=authorization_endpoint,
            token_endpoint=token_endpoint,
            jwks_uri=jwks_uri,
            registration_endpoint=registration_endpoint,
            scopes_supported=self.config.scopes,
            response_types_supported=response_types,
            response_modes_supported=None,
            grant_types_supported=grant_types,
            token_endpoint_auth_methods_supported=self.config.token_endpoint_auth_methods,
            token_endpoint_auth_signing_alg_values_supported=self.config.token_endpoint_signing_algs,
            service_documentation=self.config.service_documentation,
            ui_locales_supported=self.config.ui_locales_supported,
            op_policy_uri=self.config.op_policy_uri,
            op_tos_uri=self.config.op_tos_uri,
            revocation_endpoint=revocation_endpoint,
            revocation_endpoint_auth_methods_supported=self.config.revocation_endpoint_auth_methods,
            revocation_endpoint_auth_signing_alg_values_supported=self.config.revocation_endpoint_signing_algs,
            introspection_endpoint=introspection_endpoint,
            introspection_endpoint_auth_methods_supported=self.config.introspection_endpoint_auth_methods,
            introspection_endpoint_auth_signing_alg_values_supported=self.config.introspection_endpoint_signing_methods,
            code_challenge_methods_supported=self.get_code_challenges(),
        )

    def get_code_challenges(self) -> list[str]:
        """
        Helper method used to resolve the list of PKCE Code Challenge Methods
        supported by the Authorization Code Grant.

        :return: PKCE Code Challenge Methods of the Authorization Code Grant.
        :rtype: list[str]
        """

        grant = next(
            (
                grant
                for grant in self.config.authorization_grants
                if grant.__grant_type__ == "authorization_code"
            ),
            None,
        )

        if not grant:
            return None

        # pylint: disable=protected-access
        return list(grant._challenges.keys())
