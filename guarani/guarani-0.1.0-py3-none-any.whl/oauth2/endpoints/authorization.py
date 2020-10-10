from __future__ import annotations

from typing import Any, Optional

from guarani.oauth2.endpoints.base import BaseEndpoint
from guarani.oauth2.exceptions import (
    FatalError,
    InvalidRequest,
    OAuth2Error,
    UnauthorizedClient,
    UnsupportedResponseType,
)
from guarani.oauth2.grants import BaseGrant
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2RedirectResponse, OAuth2Request
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

    async def __call__(self, request: OAuth2Request) -> OAuth2RedirectResponse:
        """
        Creates an Authorization Response via a Redirect Response.

        Whenever a :class:`FatalError` is raised, the Provider will redirect
        the User-Agent to the its own error page, since it is too risky
        to disclose any information to an untrusted Client.

        Any other type of error is safely redirected to the Redirect URI
        provided by the Client in the Authorization Request.

        If the flow of the endpoint results in a successful response,
        it will also redirect the User-Agent to the provided Redirect URI.

        This endpoint is to be used by Grants that have an Authorization Workflow,
        and it **REQUIRES** consent given by the Resource Owner (User),
        be it implicit or explicit.

        The means of which the application obtains the consent of the Resource Owner
        has to be defined in the Framework Integration, since it usually requires
        a redirection to an endpoint that is not supported by OAuth 2.1.

        If this method is hit, it assumes that the Resource Owner has given consent
        to whatever scopes were requested by the Client.

        :param request: Current request being processed.
        :type request: OAuth2Request

        :return: Redirect Response to either the provided Redirect URI
            or the Provider's error page.
        :rtype: OAuth2RedirectResponse
        """

        data = request.data

        if not data:
            error = FatalError(description="Missing request parameters.")
            url = urlencode(self.config.error_url, **error.dump())
            return OAuth2RedirectResponse(url)

        response_type: str = data.get("response_type")
        client_id: str = data.get("client_id")
        redirect_uri: str = data.get("redirect_uri")
        state: Optional[str] = data.get("state")

        try:
            user: Any = request.user
            grant = self.validate_response_type(response_type, state)
            client = await self.validate_client(
                client_id, redirect_uri, response_type, state
            )

            response = await grant.authorize(data, client, user)
            url = urlencode(redirect_uri, **response)

            return OAuth2RedirectResponse(url)
        except FatalError as exc:
            url = urlencode(self.config.error_url, **exc.dump())
            return OAuth2RedirectResponse(url, headers=exc.headers)
        except OAuth2Error as exc:
            url = urlencode(redirect_uri, **exc.dump())
            return OAuth2RedirectResponse(url, headers=exc.headers)

    def validate_response_type(
        self, response_type: str, state: Optional[str] = None
    ) -> BaseGrant:
        """
        Validates the requested `response_type` against the set
        of registered Grants of the Provider.

        :param response_type: Response type to be validated.
        :type response_type: str

        :param state: State of the Client during the Request.
        :type state: str, optional

        :raises InvalidRequest: The `response_type` is missing or invalid.
        :raises UnsupportedResponseType: The Provider does not support
            the requested `response_type` as an Authorization Grant.

        :return: Grant that represents the requested `response_type`.
        :rtype: BaseGrant
        """

        if not response_type or not isinstance(response_type, str):
            raise InvalidRequest(
                description='Invalid parameter "response_type".', state=state
            )

        for grant in self.config.authorization_grants:
            if grant.__response_type__ == response_type:
                return grant(self.adapter, self.config)
        else:
            raise UnsupportedResponseType(
                description=f'Unsupported response_type "{response_type}".', state=state
            )

    async def validate_client(
        self,
        client_id: str,
        redirect_uri: str,
        response_type: str,
        state: Optional[str] = None,
    ) -> ClientMixin:
        """
        Validaes the `client_id` parameter to ensure that a Client exists with this ID.
        Verifies if the Client is allowed to use the provided `redirect_uri`.
        Verifies if the Client is allowed to use the requested `response_type`.

        :param client_id: ID of the Client requesting authorization.
        :type client_id: str

        :param redirect_uri: Redirect URI provided by the Client in the Request.
        :type redirect_uri: str

        :param response_type: Authorization Grant requested by the Client.
        :type response_type: str

        :param state: Client State provided in the Request, defaults to None.
        :type state: str, optional

        :raises FatalError: Raised on any of the following conditions::
            - The provided `client_id` is not a valid string.
            - The provided `redirect_uri` is not a valid string.
            - The provided Client is not registered within the Authorization Server.
            - The Client is not allowed to use the provided `redirect_uri`.
        :raises UnauthorizedClient: The Client is not allowed to use the requested Grant.

        :return: Validated Client.
        :rtype: ClientMixin
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

        if not client.validate_response_type(response_type):
            raise UnauthorizedClient(state=state)

        return client
