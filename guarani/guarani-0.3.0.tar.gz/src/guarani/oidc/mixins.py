from datetime import datetime

from guarani.oauth2 import mixins


class AuthorizationCodeMixin(mixins.AuthorizationCodeMixin):
    """
    Extends the functionality of the model of the Authorization Code
    by implementing the values used by OpenID Connect.

    The application's Authorization Code **MUST** inherit from this class
    and implement **ALL** the methods defined here and in its superclass.
    """

    def get_nonce(self) -> str:
        """
        Returns the value of the `nonce` provided by the `Client`
        in the `Authentication Request`.

        :return: Nonce value of the Client.
        :rtype: str
        """

        raise NotImplementedError

    def get_auth_time(self) -> int:
        """
        Returns the time of the authentication of the User.

        :return: Time of User authentication.
        :rtype: int
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
