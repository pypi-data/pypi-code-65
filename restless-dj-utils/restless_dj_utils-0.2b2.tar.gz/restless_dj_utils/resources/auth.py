"""
Authentication mixin for restless
"""

from django.contrib.auth import models

from restless_dj_utils.rest_sessions.models import APISession
from restless_dj_utils.exceptions import AuthenticationError


class AuthenticatedResourceMixin:
    """
    AuthenticatedResourceMixin
    """

    def is_authenticated(self):
        """
        Grab the token from Authorization header and use AuthService to
        authenticate the user.
        :return: True if authenticated otherwise False
        """

        self.request.user = models.AnonymousUser()

        token = self.request.META.get("HTTP_AUTHORIZATION")
        try:
            token = token.split(' ', 1)[1]
        except (IndexError, AttributeError):
            pass

        if not token:
            return False

        try:
            api_session, token_data = APISession.authenticate_token(token)
        except AuthenticationError:
            return False

        self.request.token = token
        self.request.token_data = token_data
        self.request.user = api_session.user
        return True


class JWTAuthenticationResourceMixin:
    """
    JWTOnlyAuthenticationResourceMixin
    """

    def is_authenticated(self):
        """
        Grab the token from Authorization header and use AuthService to
        validate the JWT token.
        :return: True if validation passes
        """

        self.request.user = models.AnonymousUser()

        token = self.request.META.get("HTTP_AUTHORIZATION")
        try:
            token = token.split(' ', 1)[1]
        except (IndexError, AttributeError):
            pass

        if not token:
            return False

        try:
            token_data = APISession.validate_token(token)
        except AuthenticationError:
            return False

        self.request.token = token
        self.request.token_data = token_data
        return True
