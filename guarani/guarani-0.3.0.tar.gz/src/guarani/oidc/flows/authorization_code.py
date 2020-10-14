from __future__ import annotations

from datetime import datetime
from typing import Any

from guarani.jose import JsonWebToken
from guarani.oauth2 import ClientMixin
from guarani.oidc.claims import IDToken
from guarani.oidc.utils import create_half_hash


class AuthorizationCodeFlow:
    """
    Extension to the Authorization Code Grant.

    This extension provides an ID Token to the requesting Client
    that describes the data of the authenticated User.

    It returns a dictionary in the format `{"id_token": "<id_token>"}`,
    which will be appended to the Token Response of the Grant.

    :param id_token_lifespan: Lifespan of the ID Token.
    :type id_token_lifespan: int
    """

    def __init__(self, id_token_lifespan: int = 36000):
        self.id_token_lifespan = id_token_lifespan

    async def post_token(self, token: dict, client: ClientMixin, user: Any) -> dict:
        """
        Hook used to append the ID Token to the Token Response.

        It is only issued if the scope `openid` is present in the allowed scopes.

        :param token: Token Response.
        :type token: dict

        :param client: Client requesting authorization/authentication.
        :type client: ClientMixin

        :param user: Currently authenticated User granting authorization.
        :type user: Any

        :return: ID Token representing the authenticated User.
        :rtype: dict
        """

        if "openid" not in token["scope"].split():
            return {}

        key_info = await self.get_key_info()

        userinfo = await self.get_userinfo(user, token["scope"].split())
        now = int(datetime.utcnow().timestamp())

        claims = IDToken(
            {
                "iss": key_info["iss"],
                "aud": client.get_client_id(),
                "exp": now + self.id_token_lifespan,
                "iat": now,
                "at_hash": create_half_hash(token["access_token"], key_info["alg"]),
                **userinfo,
            }
        )
        token = JsonWebToken(claims, {"alg": key_info["alg"], "typ": "JWT"})

        return {"id_token": token.encode(key_info["key"])}

    async def get_userinfo(self, user: Any, scopes: list[str]) -> dict:
        """
        Returns the information about the User based on the requested scopes.

        :param user: User subject of the Authentication Request.
        :type user: Any

        :param scopes: Scopes requested by the Client.
        :type scopes: list[str]

        :return: Information about the User based on the requested scopes.
        :rtype: dict
        """

        raise NotImplementedError

    async def get_key_info(self) -> dict:
        """
        Returns the information necessary to create an ID Token.

        The dictionary returned **MUST** contain the following information::

            * "key": Key used to sign the ID Token.
            * "alg": Algorithm used to create the signature the ID Token.
            * "iss": Identifier of the Issuer (usually is its Base URL).

        :return: Info to create an ID Token.
        :rtype: dict
        """

        raise NotImplementedError
