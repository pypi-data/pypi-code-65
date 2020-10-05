from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from guarani.oauth2.exceptions import (
    InvalidClientError,
    InvalidRequestError,
    InvalidScopeError,
)
from guarani.oauth2.grants.base import BaseGrant
from guarani.oauth2.mixins import ClientMixin, RefreshTokenMixin


class RefreshTokenGrant(BaseGrant):
    """
    Implementation of the `Refresh Token` grant described in the
    `OAuth 2.1 Spec <https://tools.ietf.org/html/draft-parecki-oauth-v2-1#section-6>`_.

    This grant is used by `Clients` with delegated access to get a new `Access Token`
    without the need of a new interaction with the `Resource Owner` during the
    duration of the refresh token.

    Since it issues new access tokens to clients with delegated access, it accepts
    all the client types supported by the OAuth 2.1 Spec.

    :cvar REISSUE_REFRESH_TOKEN: Defines if a new Refresh Token will be issued.
    """

    __grant_type__: str = "refresh_token"

    REISSUE_REFRESH_TOKEN: bool = False

    def validate_requested_scopes(
        self,
        token: RefreshTokenMixin,
        scopes: list[str],
        client: ClientMixin,
        state: Optional[str] = None,
    ) -> None:
        """
        Verifies if all of the requested `Scopes` are supported
        by the `Authorization Server` and if the requested scopes
        are not broader than previously granted.

        :param token: Stored Refresh Token.
        :type token: RefreshTokenMixin

        :param scopes: Requested scopes.
        :type scopes: list[str]

        :param client: Client that requested the provided scopes.
        :type client: ClientMixin

        :param state: State of the request provided by the Client, defaults to None.
        :type state: str, optional

        :raises InvalidScopeError: The Authorization Server does not support
            one or more of the requested scopes, or the requested scopes
            are broader than previously granted.
        """

        super().validate_requested_scopes(scopes, client, state)

        if any(scope not in token.get_scopes() for scope in scopes):
            raise InvalidScopeError(description="Invalid broader scope.")

    async def validate_token_request(self) -> None:
        """
        Validates the incoming data from the `Client` to ensure
        that **ALL** the required parameters were provided.

        From the specification at
        `<https://tools.ietf.org/html/draft-parecki-oauth-v2-1-03#section-6>`_::

            Authorization servers SHOULD determine, based on a risk assessment,
            whether to issue refresh tokens to a certain client. If the
            authorization server decides not to issue refresh tokens, the client
            MAY refresh access tokens by utilizing other grant types, such as the
            authorization code grant type. In such a case, the authorization
            server may utilize cookies and persistent grants to optimize the user
            experience.

            If refresh tokens are issued, those refresh tokens MUST be bound to
            the scope and resource servers as consented by the resource owner.
            This is to prevent privilege escalation by the legitimate client and
            reduce the impact of refresh token leakage.

            If the authorization server issued a refresh token to the client, the
            client makes a refresh request to the token endpoint by adding the
            following parameters using the "application/x-www-form-urlencoded"
            format per Appendix B with a character encoding of UTF-8 in the HTTP
            request entity-body:

            "grant_type": REQUIRED. Value MUST be set to "refresh_token".

            "refresh_token": REQUIRED. The refresh token issued to the client.

            "scope": OPTIONAL. The scope of the access request as described by
                Section 3.3. The requested scope MUST NOT include any scope not
                originally granted by the resource owner, and if omitted is
                treated as equal to the scope originally granted by the resource
                owner.

            Because refresh tokens are typically long-lasting credentials used to
            request additional access tokens, the refresh token is bound to the
            client to which it was issued. Confidential or credentialed clients
            MUST authenticate with the authorization server as described in
            Section 3.2.1.

            For example, the client makes the following HTTP request using
            transport-layer security (with extra line breaks for display purposes
            only):

            POST /token HTTP/1.1
            Host: server.example.com
            Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW
            Content-Type: application/x-www-form-urlencoded

            grant_type=refresh_token&refresh_token=tGzv3JOkF0XG5Qx2TlKWIA

            The authorization server MUST:

            * require client authentication for confidential or credentialed
                clients

            * authenticate the client if client authentication is included and
                ensure that the refresh token was issued to the authenticated
                client, and

            * validate the refresh token.
        """

        data = self.request.data

        if data.get("grant_type") != "refresh_token":
            raise InvalidRequestError(
                description='The grant_type MUST be "refresh_token".'
            )

        if not data.get("refresh_token") or not isinstance(
            data.get("refresh_token"), str
        ):
            raise InvalidRequestError(description='Invalid parameter "refresh_token".')

        if data.get("scope"):
            if not data.get("scope") or not isinstance(data.get("scope"), str):
                raise InvalidRequestError(description='Invalid parameter "scope".')

        self.data = {
            "grant_type": data["grant_type"],
            "refresh_token": data["refresh_token"],
            "scopes": data.get("scope").split() if data.get("scope") else None,
        }

    async def create_token_response(self) -> dict:
        """
        Validates the provided `Refresh Token` to check if its data matches
        both the `Client` and the `User`, then issues a new `Access Token` and,
        if allowed, a new `Refresh Token`, with both bound to the `Client` and `User`.

        From the specification at
        `<https://tools.ietf.org/html/draft-parecki-oauth-v2-1-03#section-5.1>`_::

            The authorization server issues an access token and optional refresh
            token, and constructs the response by adding the following parameters
            to the entity-body of the HTTP response with a 200 (OK) status code:

            "access_token": REQUIRED. The access token issued by the
                authorization server.

            "token_type": REQUIRED. The type of the token issued as described
                in Section 7.1. Value is case insensitive.

            "expires_in": RECOMMENDED. The lifetime in seconds of the access
                token. For example, the value "3600" denotes that the access
                token will expire in one hour from the time the response was
                generated. If omitted, the authorization server SHOULD provide
                the expiration time via other means or document the default value.

            "refresh_token": OPTIONAL. The refresh token, which can be used to
                obtain new access tokens using the same authorization grant as
                described in Section 6.

            "scope": OPTIONAL, if identical to the scope requested by the
                client; otherwise, REQUIRED. The scope of the access token as
                described by Section 3.3.

            The parameters are included in the entity-body of the HTTP response
            using the "application/json" media type as defined by [RFC7159]. The
            parameters are serialized into a JavaScript Object Notation (JSON)
            structure by adding each parameter at the highest structure level.
            Parameter names and string values are included as JSON strings.
            Numerical values are included as JSON numbers. The order of
            parameters does not matter and can vary.

            The authorization server MUST include the HTTP "Cache-Control"
            response header field [RFC7234] with a value of "no-store" in any
            response containing tokens, credentials, or other sensitive
            information, as well as the "Pragma" response header field [RFC7234]
            with a value of "no-cache".

            For example:

            HTTP/1.1 200 OK
            Content-Type: application/json
            Cache-Control: no-store
            Pragma: no-cache

            {
                "access_token": "2YotnFZFEjr1zCsicMWpAA",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
                "example_parameter": "example_value"
            }

            The client MUST ignore unrecognized value names in the response.  The
            sizes of tokens and other values received from the authorization
            server are left undefined. The client should avoid making
            assumptions about value sizes. The authorization server SHOULD
            document the size of any value it issues.

        :return: Access Token and its metadata, optionally with a Refresh Token.
        :rtype: dict
        """

        client = self.request.client
        data = self.data

        token = await self.get_refresh_token(data["refresh_token"])

        if not token:
            raise InvalidRequestError(description="Invalid Refresh Token.")

        self.validate_refresh_token(data, token, client)

        scopes = data["scopes"] if data["scopes"] else token.get_scopes()
        user = await self.get_user(token)

        access_token = await self.adapter.create_access_token(client, user, scopes)
        refresh_token = (
            await self.adapter.create_refresh_token(client, user, scopes)
            if self.REISSUE_REFRESH_TOKEN
            and client.validate_grant_type("refresh_token")
            else None
        )

        return self.create_token(
            access_token,
            self.config.token_lifespan,
            refresh_token,
            scopes if scopes != token.get_scopes() else None,
        )

    def validate_refresh_token(
        self,
        data: dict,
        token: RefreshTokenMixin,
        client: ClientMixin,
    ) -> None:
        """
        Validates the data of the `Provided Refresh Token` against both
        the current `Client` and the `Stored Refresh Token`.

        :param data: Provided Refresh Token.
        :type data: dict

        :param code: Stored Refresh Token.
        :type code: RefreshTokenMixin

        :param client: Current Client requesting an Access Token.
        :type client: ClientMixin
        """

        if token.get_client_id() != client.get_client_id():
            raise InvalidClientError

        if datetime.utcnow() >= token.get_expiration():
            raise InvalidRequestError(description="Refresh Token expired.")

        if not data["scopes"]:
            return

        self.validate_requested_scopes(token, data["scopes"], client)

    async def get_refresh_token(self, refresh_token: str) -> RefreshTokenMixin:
        """
        Retrieves the data of a `Refresh Token` from the application's storage
        based on the provided `refresh_token`.

        :param refresh_token: Refresh Token to be fetched.
        :type refresh_token: str

        :return: Requested Refresh Token.
        :rtype: RefreshTokenMixin
        """

        raise NotImplementedError

    async def get_user(self, refresh_token: RefreshTokenMixin) -> Any:
        """
        Retrieves the `User` bound to the current `Refresh Token`.

        :param refresh_token: Current Refresh Token.
        :type refresh_token: RefreshTokenMixin

        :return: User bound to the Refresh Token.
        :rtype: Any
        """

        raise NotImplementedError
