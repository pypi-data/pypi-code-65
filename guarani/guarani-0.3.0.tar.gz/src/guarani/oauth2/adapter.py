from __future__ import annotations

from typing import Any

from guarani.oauth2.mixins import ClientMixin


class BaseAdapter:
    async def find_client(self, client_id: str) -> ClientMixin:
        """
        Searches for a client in the application's storage
        and returns it if it succeeds, otherwise returns None.

        :param client_id: ID of the client being searched.
        :type client_id: str

        :return: Client based on the provided ID.
        :rtype: ClientMixin
        """

        raise NotImplementedError

    async def create_access_token(
        self, client: ClientMixin, resource_owner: Any, scopes: list[str]
    ) -> str:
        """
        Generates an `Access Token` that creates a tight coupling between the `Client`,
        the `Resource Owner` and the `Scopes` that the `Resource Owner`
        authorized the `Client` to access on its behalf.

        The structure of the `Access Token` is left undefined by this framework,
        but it is **RECOMMENDED** that the application uses `Json Web Token (JWT)`
        for the `Access Token`, followin the specifications at
        `JWT Profile for OAuth 2 Access Tokens
        <https://tools.ietf.org/html/draft-ietf-oauth-access-token-jwt>`_.

        The format of the `Access Token Response` is as follows, with values displayed
        as example only, not defining a format for any of the Tokens::

            {
                "access_token": "vlOa11kBoziWFBsQiUu59SjgHJbi7spU80Ew5xCTZ9UhZmWN",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "7eqGioGLs-O7ky3CgeAU87bfijRam6r5"
            }

        Since the `Refresh Token` is optional when the `Resource Owner`
        is separate from the `Client`, and not recommended
        when the `Client` is the `Resource Owner`, its presence
        in the final response is optional.

        :param client: Client that will use the issued Access Token.
        :type client: ClientMixin

        :param resource_owner: Resource Owner that the Client is acting on behalf of.
        :type resource_owner: Any

        :param scopes: Scopes of the Token granted by the Resource Owner to the Client.
        :type scopes: list[str]

        :return: Issued Access Token.
        :rtype: str
        """

        raise NotImplementedError

    async def create_refresh_token(
        self, client: ClientMixin, resource_owner: Any, scopes: list[str]
    ) -> str:
        """
        Generates a `Refresh Token` binding the `Client` and the `Resource Owner`,
        together with the `Scopes` granted by the `Resource Owner`,
        and sets its expiration to the value of the argument `expiration_in_days`.

        :param client: Client to whom the Refresh Token was issued to.
        :type client: ClientMixin

        :param resource_owner: Resource Owner represented by the Client.
        :type resource_owner: Any

        :param scopes: Scopes of the next Access Token issued by this Refresh Token.
        :type scopes: list[str]

        :return: Issued Refresh Token.
        :rtype: str
        """

        raise NotImplementedError
