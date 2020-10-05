from __future__ import annotations

from typing import Type

from guarani.oauth2.endpoints.base import BaseEndpoint
from guarani.oauth2.exceptions import (
    InvalidRequestError,
    OAuth2Error,
    UnauthorizedClientError,
    UnsupportedGrantTypeError,
)
from guarani.oauth2.grants.base import BaseGrant
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2JSONResponse


class TokenEndpoint(BaseEndpoint):
    """
    Endpoint used by the client to exchange an authorization grant,
    or its own credentials for an access token that will be used by
    the client to act on behalf of the Resource Owner.

    This endpoint requires some kind of `Client Authentication`.
    The methods used to authenticate or validate the Client **MUST**
    be defined by the `Grants` that make use of this endpoint
    via the Grant attribute :attr:`__authenticate_methods__`.
    """

    __endpoint__: str = "token"

    _headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}

    async def __call__(self) -> OAuth2JSONResponse:
        try:
            await self.validate_request()
            return await self.create_response()
        except OAuth2Error as exc:
            headers = exc.headers
            headers.update(self._headers)
            return OAuth2JSONResponse(400, headers, exc.dump())

    async def validate_request(self) -> None:
        """
        Validates the `Token Request` of the `Client` by making sure
        the required parameter "grant_type" is present, and that the
        `Client` can authenticate with the allowed authentication methods.

        :raises InvalidRequestError: From :meth:`validate_grant_type`.
        :raises UnsupportedGrantTypeError: From :meth:`validate_grant_type`.
        :raises InvalidClientError: The Client failed to authenticate itself.
        :raises UnauthorizedClientError: The Client cannot use the requested Grant.
        """

        grant_type = self.request.data.get("grant_type")
        grant = self.validate_grant_type(grant_type)

        await self.client_auth(self.request, grant.__authentication_methods__)

        client: ClientMixin = self.request.client

        if not client.validate_grant_type(grant_type):
            raise UnauthorizedClientError

        # pylint: disable=attribute-defined-outside-init
        self.grant = grant(self.request, self.adapter, self.config)

    async def create_response(self) -> OAuth2JSONResponse:
        """
        Creates an `Token Response` to the `Client`
        with the result of the `Token Process`.

        The `Token Response` is a JSON object returned from the `Token Endpoint`.

        The data returned by the `Successful Response` can be found at
        `<https://tools.ietf.org/html/draft-parecki-oauth-v2-1-03#section-5.1>`_,
        while the data returned by the `Failure Response` can be found at
        `<https://tools.ietf.org/html/draft-parecki-oauth-v2-1-03#section-5.2>`_.

        :return: JSON Response with the data of the Access Token or of the error.
        :rtype: OAuth2JSONResponse
        """

        await self.grant.validate_token_request()
        data = await self.grant.create_token_response()
        return OAuth2JSONResponse(200, self._headers, data)

    def validate_grant_type(self, grant_type: str) -> Type[BaseGrant]:
        """
        Validates the requested `grant_type` against the set
        of registered Grants of the Provider.

        :param grant_type: Response type to be validated.
        :type grant_type: str

        :raises InvalidRequestError: The `grant_type` is missing or invalid.
        :raises UnsupportedGrantTypeError: The Provider does not support
            the requested `grant_type` as a Token Grant.

        :return: Grant class that represents the requested `grant_type`.
        :rtype: Type[BaseGrant]
        """

        if not grant_type or not isinstance(grant_type, str):
            raise InvalidRequestError(description='Invalid parameter "grant_type".')

        for grant in self.config.token_grants:
            if grant.__grant_type__ == grant_type:
                return grant
        else:
            raise UnsupportedGrantTypeError(
                description=f'Unsupported grant_type "{grant_type}".'
            )
