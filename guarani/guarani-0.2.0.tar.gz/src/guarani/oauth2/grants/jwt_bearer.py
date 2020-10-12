from typing import Any
from urllib.parse import urljoin

from guarani.jose import JoseError, JsonWebKey, JsonWebToken
from guarani.oauth2.exceptions import InvalidGrant, InvalidRequest
from guarani.oauth2.grants.base import BaseGrant
from guarani.oauth2.mixins import ClientMixin


class JWTBearerGrant(BaseGrant):
    """
    Implementation of the JWT Grant described in
    `JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication
    and Authorization Grants <https://tools.ietf.org/html/rfc7523>`_.

    In this Grant, the Client provides an `Assertion` in the `JWT format`, signed
    with the Private Key of an Issuer that is trusted by the Authorization Server.

    This Assertion contains the ID of the User represented by the Client, the
    identifier of the Issuer (usually an URL), the Audience of the Assertion,
    that **MUST** be the Provider's Token Endpoint, an Expiration timestamp
    indicating until when the Assertion is valid and, optionnaly, other claims
    supported by either JWT or the Provider.
    """

    __grant_type__: str = "urn:ietf:params:oauth:grant-type:jwt-bearer"

    async def token(self, data: dict, client: ClientMixin) -> dict:
        """
        Validates the provided `JWT Assertion` to check if its data matches
        the `Client`, then issues a new `Access Token` bound to the `Client`.

        :param data: Data of the Token Request.
        :type data: dict

        :param client: Client requesting a new Token.
        :type client: ClientMixin

        :return: Access Token and its metadata, optionally with a Refresh Token.
        :rtype: dict
        """

        data = self.validate_token_request(data)

        self.validate_requested_scopes(data.get("scopes"), client)

        options = {
            "iss": {"essential": True},
            "sub": {"essential": True},
            "aud": {"essential": True},
            "exp": {"essential": True},
            "jti": {"essential": True},
        }

        try:
            assertion = JsonWebToken.decode(
                data["assertion"], None, validate=False, options=options
            )
        except JoseError as exc:
            raise InvalidGrant(exc.error) from exc

        key = await self.get_issuer_public_key(assertion.header, assertion.claims)

        try:
            claims = JsonWebToken.decode(data["assertion"], key, options=options).claims
        except JoseError as exc:
            raise InvalidGrant(exc.error) from exc

        token_endpoint = urljoin(self.config.issuer, self.config.token_endpoint)

        if claims["aud"] != token_endpoint:
            raise InvalidGrant("Invalid Audience.")

        scopes = client.get_allowed_scopes(data.get("scopes"))
        user = await self.authenticate_user(claims, client)
        token = await self.adapter.create_access_token(client, user, scopes)

        return self.create_token(
            token,
            self.config.token_lifespan,
            None,
            scopes if scopes != data.get("scopes") else None,
        )

    def validate_token_request(self, data: dict) -> dict:
        """
        Validates the incoming data from the `Client` to ensure
        that **ALL** the required parameters were provided.

        From the specification at `<https://tools.ietf.org/html/rfc7523#section-2.1>`_::

            To use a Bearer JWT as an authorization grant, the client uses an
            access token request as defined in Section 4 of the OAuth Assertion
            Framework [RFC7521] with the following specific parameter values and
            encodings.

            The value of the "grant_type" is "urn:ietf:params:oauth:grant-
            type:jwt-bearer".

            The value of the "assertion" parameter MUST contain a single JWT.

            The "scope" parameter may be used, as defined in the OAuth Assertion
            Framework [RFC7521], to indicate the requested scope.

            Authentication of the client is optional, as described in
            Section 3.2.1 of OAuth 2.0 [RFC6749] and consequently, the
            "client_id" is only needed when a form of client authentication that
            relies on the parameter is used.

            The following example demonstrates an access token request with a JWT
            as an authorization grant (with extra line breaks for display
            purposes only):

                POST /token.oauth2 HTTP/1.1
                Host: as.example.com
                Content-Type: application/x-www-form-urlencoded

                grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer
                &assertion=eyJhbGciOiJFUzI1NiIsImtpZCI6IjE2In0.
                eyJpc3Mi[...omitted for brevity...].
                J9l-ZhwP[...omitted for brevity...]

        :param data: Data of the Token Request.
        :type data: dict

        :return: Validated and reformatted Token Request data.
        :rtype: dict
        """

        if data.get("grant_type") != self.__grant_type__:
            raise InvalidRequest(f'The grant_type MUST be "{self.__grant_type__}".')

        if not data.get("assertion") or not isinstance(data.get("assertion"), str):
            raise InvalidRequest('Missing "assertion" in request.')

        if data.get("scope"):
            if not data.get("scope") or not isinstance(data.get("scope"), str):
                raise InvalidRequest('Invalid parameter "scope".')

        return {
            "grant_type": data["grant_type"],
            "assertion": data["assertion"],
            "scopes": data.get("scope").split() if data.get("scope") else [],
        }

    async def get_issuer_public_key(self, headers: dict, payload: dict) -> JsonWebKey:
        """
        Returns the `Public Key` of the `Issuer` of the Assertion
        if it is trusted by the application, otherwise returns None.

        This method **MUST** return the appropriate `Public Key` wrapped
        in a :class:`guarani.jose.JsonWebKey` object to be used to decode
        the assertion presented by the Client.

        To implement this method, the application needs to address
        at least the following parameters::

            * "iss" - Issuer of the Assertion in the Payload.
            * "kid" - ID of the Public Key used to verify the Signature of the Sssertion.

        The application **MUST** implement this method.

        :param headers: Headers of the JWT Assertion.
            Can be used to retrieve the `Key's ID`.
        :type headers: dict

        :param payload: Payload of the JWT Assertion.
            Can be used to retrieve the `Issuer's ID`.
        :type payload: dict

        :return: Public key of the Issuer of the Assertion.
        :rtype: JsonWebKey
        """

        raise NotImplementedError

    async def authenticate_user(self, claims: dict, client: ClientMixin) -> Any:
        """
        Returns the instance of the `User` represented by the `Assertion`
        if the `Client` holder of the Assertion is allowed to represent it.

        The ID of the user is located at `claims["sub"]`.

        :param claims: Claims of the Assertion.
        :type claims: dict

        :param client: Client claiming to represent the User of the Assertion.
        :type client: ClientMixin

        :return: Instance of the User represented by the Assertion.
        :rtype: Any
        """

        raise NotImplementedError
