from __future__ import annotations

from typing import Optional, Type

from guarani.oauth2.endpoints.base import BaseEndpoint
from guarani.oauth2.exceptions import (
    FatalError,
    InvalidRequestError,
    OAuth2Error,
    UnauthorizedClientError,
    UnsupportedResponseTypeError,
)
from guarani.oauth2.grants.base import BaseGrant
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2RedirectResponse
from guarani.webtools import urlencode


class AuthorizationEndpoint(BaseEndpoint):
    """
    Endpoint used to get the consent of the Resource Owner on the scopes that
    a client is requesting to act on his/her behalf.

    Since the OAuth 2.1 Spec does not define the need for authentication when
    using this endpoint, it was left omitted. If there is a need for it in
    the application, feel free to subclass this endpoint and define the
    authentication methods that best suit your needs.
    """

    __endpoint__: str = "authorization"

    async def __call__(self) -> OAuth2RedirectResponse:
        try:
            await self.validate_request()
            return await self.create_response()
        except FatalError as exc:
            return OAuth2RedirectResponse(
                url=urlencode(self.config.error_url, **exc.dump()),
                status=400,
            )
        except OAuth2Error as exc:
            return OAuth2RedirectResponse(
                url=urlencode(self.request.data["redirect_uri"], **exc.dump()),
                status=400,
            )

    async def validate_request(self) -> None:
        """
        Validates the `Authorization Request` of the `Client` by making sure
        the required parameters were provided.

        The following parameters are **REQUIRED**::

            * "response_type": Used to select the appropriate Grant.
            * "client_id": Used to identify the Client making the Request.
            * "redirect_uri": URI of the Client used to get the response of the Grant.

        If any of the previous parameters are not present, the `Provider`
        responds with an error message and an error description.

        :raises UnauthorizedClientError: The Client cannot use the requested Grant.
        """

        data = self.request.data

        if not data:
            raise FatalError(description="Invalid query string.")

        await self.validate_client(data.get("client_id"), data.get("redirect_uri"))

        grant = self.validate_response_type(
            data.get("response_type"),
            data.get("state"),
        )

        client: ClientMixin = self.request.client

        if not client.validate_response_type(data["response_type"]):
            raise UnauthorizedClientError

        # pylint: disable=attribute-defined-outside-init
        self.grant = grant(self.request, self.adapter, self.config)

    async def create_response(self) -> OAuth2RedirectResponse:
        """
        Creates an `Authorization Response` to the `Client` with the result
        of the `Authorization Process`.

        The specific parameters returned can be found on the documentation
        of each supported `Authorization Grant`.

        The `Authorization Response` is a redirection to either the Client's
        `redirect_uri` or the error page of the `Provider`.

        :return: Redirect Response to either the Client's or the Provider's URI.
        :rtype: OAuth2RedirectResponse
        """

        await self.grant.validate_authorization_request()
        url = await self.grant.create_authorization_response()
        return OAuth2RedirectResponse(url=url)

    async def validate_client(self, client_id: str, redirect_uri: str) -> None:
        """
        Validates the `client_id` parameter to ensure that a Client exists with this ID.

        Validates the `redirect_uri` parameter to ensure that the Client
        has the provided URI registered as its own.

        :param client_id: ID of the Client requesting authorization.
        :type client_id: str

        :param redirect_uri: Redirect URI of the Client.
        :type redirect_uri: str

        :raises FatalError: Raised on any of the following conditions::
            - "client_id" is not a valid string.
            - "redirect_uri" is not a valid string.
            - Client is not registered within the Authorization Server.
            - Redirect URI is not registered for the specific Client.
        """

        if not client_id or not isinstance(client_id, str):
            raise FatalError(description='Invalid parameter "client_id".')

        if not redirect_uri or not isinstance(redirect_uri, str):
            raise FatalError(description='Invalid parameter "redirect_uri".')

        client = await self.adapter.find_client(client_id)

        if not client:
            raise FatalError(description="Invalid client.")

        if not client.validate_redirect_uri(redirect_uri):
            raise FatalError(description="Invalid Redirect URI.")

        self.request.client = client

    def validate_response_type(
        self,
        response_type: str,
        state: Optional[str] = None,
    ) -> Type[BaseGrant]:
        """
        Validates the requested `response_type` against the set
        of registered Grants of the Provider.

        Verifies if the Client is allowed to use the requested `response_type`.

        :param response_type: Response type to be validated.
        :type response_type: str

        :param state: State of the Client during the Request.
        :type state: str, optional

        :raises InvalidRequestError: The `response_type` is missing or invalid.
        :raises UnsupportedResponseTypeError: The Provider does not support
            the requested `response_type` as an Authorization Grant.

        :return: Grant class that represents the requested `response_type`.
        :rtype: Type[BaseGrant]
        """

        if not response_type or not isinstance(response_type, str):
            raise InvalidRequestError(
                description='Invalid parameter "response_type".',
                state=state,
            )

        for grant in self.config.authorization_grants:
            if grant.__response_type__ == response_type:
                return grant
        else:
            raise UnsupportedResponseTypeError(
                description=f'Unsupported response_type "{response_type}".',
                state=state,
            )
