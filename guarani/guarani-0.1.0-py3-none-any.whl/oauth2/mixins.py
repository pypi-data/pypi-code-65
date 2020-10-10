from __future__ import annotations

from datetime import datetime

from guarani.jose import JsonWebKey


class AuthorizationCodeMixin:
    """
    Defines the model of the Authorization Code used by this framework.

    The application's Authorization Code **MUST** inherit from this class
    and implement **ALL** the methods defined here.
    """

    def get_client_id(self) -> str:
        """
        Returns the `ID` of the `Client` that requested the `Authorization Grant`.

        :return: ID of the Client from this Authorization Code.
        :rtype: str
        """

        raise NotImplementedError

    def get_user_id(self) -> str:
        """
        Returns the `ID` of the `User` that issued the current `Authorization Grant`.

        :return: ID of the User from this Authorization Code.
        :rtype: str
        """

        raise NotImplementedError

    def get_redirect_uri(self) -> str:
        """
        Returns the `Redirect URI` of the current `Authorization Code`.

        :return: Redirect URI.
        :rtype: str
        """

        raise NotImplementedError

    def get_scopes(self) -> list[str]:
        """
        Returns the `Scopes` that were authorized by the `User` to the `Client`.

        :return: Authorized Scopes.
        :rtype: list[str]
        """

        raise NotImplementedError

    def get_code_challenge(self) -> str:
        """
        Returns the `Code Challenge` provided by the `Client`.

        :return: Code Challenge.
        :rtype: str
        """

        raise NotImplementedError

    def get_code_challenge_method(self) -> str:
        """
        Returns the `Code Challenge Method` used by the `Client`.

        :return: Code Challenge Method.
        :rtype: str
        """

        raise NotImplementedError

    def get_expiration(self) -> datetime:
        """
        Returns a datetime representing the expiration of the `Authorization Code`.

        :return: Time when the Authorization Code expires.
        :rtype: datetime
        """

        raise NotImplementedError


class ClientMixin:
    """
    Defines the model of the Client used by this framework.

    The application's Client **MUST** inherit from this class and implement
    **ALL** the methods defined here.
    """

    def get_client_id(self) -> str:
        """
        Returns the `ID` of the `Client`.

        :return: ID of the Client.
        :rtype: str
        """

        raise NotImplementedError

    def get_client_secret(self) -> str:
        """
        Returns the `Secret` of the `Client`.

        :return: Secret of the Client.
        :rtype: str
        """

        raise NotImplementedError

    def get_client_public_key(self, key_id: str) -> JsonWebKey:
        """
        Returns an instance of the Client's Public Key
        based on the provided Key ID or the default key.

        :param key_id: ID of the Public Key to be retrieved.
        :type key_id: str

        :return: Instance of the Client's (default) Public Key.
        :rtype: JsonWebKey
        """

        raise NotImplementedError

    def get_allowed_scopes(self, scopes: list[str]) -> list[str]:
        """
        Returns the `Scopes` that the `Client` is allowed to used
        based on the requested scopes.

        :param scopes: Requested scopes.
        :type scopes: list[str]

        :return: Scopes that the Client is allowed to request.
        :rtype: list[str]
        """

        raise NotImplementedError

    def validate_client_secret(self, client_secret: str) -> bool:
        """
        Validates the provided `client_secret` in the `Client Authentication`
        against the `Client Secret` of the Client stored in the database.

        :param client_secret: Provided Secret to be validated.
        :type client_secret: str

        :return: The provided secret matches the Client's one.
        :rtype: bool
        """

        raise NotImplementedError

    def validate_redirect_uri(self, redirect_uri: str) -> bool:
        """
        Validates the provided `redirect_uri` against the `Redirect URIs`
        of the Client stored in the database.

        :param redirect_uri: Provided Redirect URI to be validated.
        :type redirect_uri: str

        :return: The Client is allowed to use the provided URL.
        :rtype: bool
        """

        raise NotImplementedError

    def get_token_endpoint_auth_method(self) -> str:
        """
        Returns the `Token Endpoint Auth Method` of the Client stored in the database.

        :return: Token Endpoint Authentication Method of the Client.
        :rtype: str
        """

        raise NotImplementedError

    def validate_grant_type(self, grant_type: str) -> bool:
        """
        Validates the provided `grant_type` against the `Grant Types`
        of the Client stored in the database.

        :param grant_type: Provided Grant Type to be validated.
        :type grant_type: str

        :return: The Client is allowed to use the provided Grant Type.
        :rtype: bool
        """

        raise NotImplementedError

    def validate_response_type(self, response_type: str) -> bool:
        """
        Validates the provided `response_type` against the `Response Types`
        of the Client stored in the database.

        :param response_type: Provided Response Type to be validated.
        :type response_type: str

        :return: The Client is allowed to use the provided Response Type.
        :rtype: bool
        """

        raise NotImplementedError


class RefreshTokenMixin:
    """
    Defines the model of the Refresh Token used by this framework.

    The application's Refresh Token **MUST** inherit from this class
    and implement **ALL** the methods defined here.
    """

    def get_refresh_token(self) -> str:
        """
        Returns the string that represents the `Refresh Token` object.

        :return: Refresh Token value.
        :rtype: str
        """

        raise NotImplementedError

    def get_client_id(self) -> str:
        """
        Returns the `ID` of the `Client` bound to the `Refresh Token`.

        :return: ID of the Client from this Refresh Token.
        :rtype: str
        """

        raise NotImplementedError

    def get_user_id(self) -> str:
        """
        Returns the `ID` of the `User` bound to the current `Refresh Token`.

        :return: ID of the User from this Refresh Token.
        :rtype: str
        """

        raise NotImplementedError

    def get_scopes(self) -> list[str]:
        """
        Returns the `Scopes` that were authorized by the `User` to the `Client`.

        :return: Authorized Scopes.
        :rtype: list[str]
        """

        raise NotImplementedError

    def get_expiration(self) -> datetime:
        """
        Returns a datetime representing the expiration of the `Refresh Token`.

        :return: Time when the Refresh Token expires.
        :rtype: datetime
        """

        raise NotImplementedError


class SessionMixin:
    """
    Defines the model of the User Session used by this framework.

    The application's User Session **MUST** inherit from this class
    and implement **ALL** the methods defined here.
    """

    def get_session_id(self) -> str:
        """
        Returns the ID of the current active session.

        :return: ID of the session.
        :rtype: str
        """

        raise NotImplementedError

    def get_user_id(self) -> str:
        """
        Returns the ID of the authenticated user.

        :return: ID of the user.
        :rtype: str
        """

        raise NotImplementedError

    def get_auth_time(self) -> datetime:
        """
        Returns a datetime object representing the moment when the session was created.

        :return: Creation of the session.
        :rtype: datetime
        """

        raise NotImplementedError
