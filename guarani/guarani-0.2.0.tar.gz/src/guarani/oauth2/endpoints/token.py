from guarani.oauth2.endpoints.base import BaseEndpoint
from guarani.oauth2.exceptions import (
    InvalidRequest,
    OAuth2Error,
    UnauthorizedClient,
    UnsupportedGrantType,
)
from guarani.oauth2.grants import BaseGrant
from guarani.oauth2.models import OAuth2JSONResponse, OAuth2Request


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

    async def __call__(self, request: OAuth2Request) -> OAuth2JSONResponse:
        """
        Creates a Token Response via a JSON Response.

        This endpoint is responsible for issuing Tokens to Clients
        that succeed to authenticate within the Authorization Server
        and has the necessary consent of the Resource Owner.

        This endpoint is to be used by Grants that have a Token Workflow,
        and it will return a JSON object as a result.

        If the Client fails to authenticate within the Authorization Server,
        does not have the consent of the Resource Owner or provides invalid
        or insufficient request parameters, it will receive a `400 Bad Request`
        Error Response with a JSON object describing the error.

        If the flow succeeds, the Client will then receive its Token
        in a JSON object containing the Access Token, the Token Type,
        the Lifespan of the Access Token and an optional Refresh Token,
        as well as an optional Scope parameter if the granted scopes
        differ from the requested ones.

        :param request: Current request being processed.
        :type request: OAuth2Request

        :return: Token Response and its metadata.
        :rtype: OAuth2JSONResponse
        """

        try:
            data = request.data

            if not data:
                raise InvalidRequest(description="Missing request parameters.")

            grant_type: str = data.get("grant_type")

            grant = self.validate_grant_type(grant_type)
            client = await self.authenticate(request, grant.__authentication_methods__)

            if not client.validate_grant_type(grant_type):
                raise UnauthorizedClient

            response = await grant.token(data, client)
            return OAuth2JSONResponse(200, self._headers, response)
        except OAuth2Error as exc:
            headers = exc.headers
            headers.update(self._headers)
            return OAuth2JSONResponse(400, headers, exc.dump())

    def validate_grant_type(self, grant_type: str) -> BaseGrant:
        """
        Validates the requested `grant_type` against the set
        of registered Grants of the Provider.

        :param grant_type: Response type to be validated.
        :type grant_type: str

        :raises InvalidRequest: The `grant_type` is missing or invalid.
        :raises UnsupportedGrantType: The Provider does not support
            the requested `grant_type` as a Token Grant.

        :return: Grant that represents the requested `grant_type`.
        :rtype: BaseGrant
        """

        if not grant_type or not isinstance(grant_type, str):
            raise InvalidRequest(description='Invalid parameter "grant_type".')

        for grant in self.config.token_grants:
            if grant.__grant_type__ == grant_type:
                return grant(self.adapter, self.config)
        else:
            raise UnsupportedGrantType(
                description=f'Unsupported grant_type "{grant_type}".'
            )
