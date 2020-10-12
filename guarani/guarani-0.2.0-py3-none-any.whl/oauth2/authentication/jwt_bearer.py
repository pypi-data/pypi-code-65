from urllib.parse import urljoin

from guarani.jose import JoseError, JsonWebKey, JsonWebToken
from guarani.oauth2.authentication.base import BaseClientAuthentication
from guarani.oauth2.exceptions import InvalidClient
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2Request
from guarani.webtools import to_bytes


class JWTBearer(BaseClientAuthentication):
    """
    Implements the Client Authentication via the JWT Client Assertion
    in the Body of the Request.

    If this workflow is enabled, it will look at the body of the request
    for a scheme similar to the following (line breaks for display purposes only)::

        client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3A
        client-assertion-type%3Ajwt-bearer&
        client_assertion=eyJhbGciOiJSUzI1NiIsImtpZCI6IjIyIn0.
        eyJpc3Mi[...omitted for brevity...].
        cC4hiUPo[...omitted for brevity...]

    The request's body often comes with more information that may pertain to
    a specific endpoint or authorization grant. In this case,
    the body will be similar to the following::

        grant_type=authorization_code&
        code=n0esc3NRze7LTCu7iYzS6a5acc3f0ogp4&
        client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3A
        client-assertion-type%3Ajwt-bearer&
        client_assertion=eyJhbGciOiJSUzI1NiIsImtpZCI6IjIyIn0.
        eyJpc3Mi[...omitted for brevity...].
        cC4hiUPo[...omitted for brevity...]

    The Client **MUST** be registered with a `token_endpoint_auth_method` value
    of either `client_secret_jwt` or `private_key_jwt` to use this method.

    .. note:: This method used the method
        :meth:`guarani.oauth2.mixins.ClientMixin.get_assertion_key` to retrieve
        the Client's Public Key registered within the Provider if it uses the
        method `private_key_jwt`, or it uses the Client's Secret if the method
        is `client_secret_jwt` to verify the signature of the JWT Assertion.

    If the application wants to support this Authentication method,
    it **MUST** implement its abstract method :meth:`validate_assertion`
    to validate the Assertion claims against its own configuration
    and against the Client currently authenticating.
    """

    __method__: str = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"

    async def authenticate(self, request: OAuth2Request) -> ClientMixin:
        body = request.form()

        client_assertion_type = body.get("client_assertion_type")
        client_assertion = body.get("client_assertion")

        if client_assertion_type != self.__method__:
            return None

        try:
            assertion = JsonWebToken.decode(client_assertion, None, validate=False)
        except JoseError as exc:
            raise InvalidClient(exc.error) from exc

        client = await self.find_client(assertion.claims.get("sub"))

        if not client:
            return None

        if client.get_token_endpoint_auth_method() not in (
            "client_secret_jwt",
            "private_key_jwt",
        ):
            raise InvalidClient(
                f'This Client is not allowed to use the method "{self.__method__}".'
            )

        key = await self.get_client_key(assertion.header, client)

        if not key:
            raise InvalidClient("Could not find a valid key to validate the assertion.")

        try:
            options = {
                "iss": {"essential": True},
                "sub": {"essential": True},
                "aud": {"essential": True},
                "exp": {"essential": True},
                "jti": {"essential": True},
            }
            claims = JsonWebToken.decode(client_assertion, key, options=options).claims
        except JoseError as exc:
            raise InvalidClient(exc.error) from exc

        if claims["iss"] != client.get_client_id():
            raise InvalidClient("Mismatching Issuer.")

        if claims["sub"] != client.get_client_id():
            raise InvalidClient("Mismatching Subject.")

        token_endpoint = urljoin(self.config.issuer, self.config.token_endpoint)

        if claims["aud"] != token_endpoint:
            raise InvalidClient("Mismatching Audience.")

        await self.validate_claims(claims)

        return client

    async def get_client_key(self, headers: dict, client: ClientMixin) -> JsonWebKey:
        """
        Returns the key of the Client used to verify the assertion presented.

        If the Client is registered with a `Token Endpoint Authentication Method`
        of `client_secret_jwt`, this method **MUST** return the `Client's Secret`.
        If it is registered with `private_key_jwt`, this method **MUST** return
        the `Client's Public Key`.

        Whichever method is registered for the Client, this method **MUST** return
        the appropriate value wrapped in a :class:`guarani.jose.JsonWebKey` object
        to be used to decode the assertion presented by the Client.

        The application **MAY** choose to reimplement this method if the default
        implementation does not fit its needs.

        :param headers: Headers of the JWT Assertion. Can be used to retrieve a `Key ID`.
        :type headers: dict

        :param client: Current Client presenting the assertion to authenticate.
        :type client: ClientMixin

        :return: Client's Secret or Public Key wrapped in a JsonWebKey object.
        :rtype: JsonWebKey
        """

        if client.get_token_endpoint_auth_method() == "client_secret_jwt":
            return JsonWebKey.parse(
                to_bytes(client.get_client_secret()), "oct", False, format="der"
            )

        return client.get_client_public_key(headers.get("kid"))

    async def validate_claims(self, claims: dict):
        """
        Method used to validate the `Assertion Claims` about the Client.

        The application **MUST** implement this method in order
        to provide validation to the cases listed below.

        It is **REQUIRED** for the application to verify the following claim::

            * "jti" - Certify that the same assertion is not being replayed for the time
                it is valid or for the allowed expiration time of the application.

        It is **RECOMMENDED** for the application to verify the following claims::

            * "exp" - Certify that the expiration is not unreasonably far in the future.
            * "iat" - Certify that the issuing time is not unreasonably far in the past.

        It is **RECOMMENDED** that the application validates any custom paramerets
        it supports.

        .. note:: The values of `sub` and `aud` are automatically validated
            by Guarani and **MUST NOT** be revalidated by this method.

        :param claims: Claims of the Assertion provided by the Client.
        :type claims: dict
        """

        raise NotImplementedError
