"""
Session model and manager
"""
import logging

from copy import deepcopy
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import module_loading

from restless_dj_utils.rest_sessions.conf import API_SESSION_MANAGER
from restless_dj_utils.exceptions import AuthenticationError, SessionExpiredError


logger = logging.getLogger(__name__)


def _get_session_manager():
    return module_loading.import_string(API_SESSION_MANAGER)()


class APISession(models.Model):
    """A authentication session for the API"""

    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_sessions")
    is_active = models.BooleanField(default=True)

    remote_address = models.GenericIPAddressField()
    user_agent = JSONField(default=dict, blank=True)

    description = models.CharField(default='', blank=True, max_length=255)
    token_data = JSONField(default=dict, blank=True)

    objects = _get_session_manager()

    class Meta:
        ordering = ["-created"]
        get_latest_by = ["created"]
        verbose_name = "API session"
        verbose_name_plural = "API sessions"
        app_label = "rest_sessions"

    def __str__(self):
        return f"Session for {self.user}"

    def get_token_data(self):
        token_data = deepcopy(self.token_data)
        token_data.update({
            'user_id': self.user.pk,
            'session_id': self.pk})
        return token_data

    @classmethod
    def authenticate_user(cls, username, password, remote_address, user_agent, **kwargs):
        """
        Authenticates a user with django authenticate method, creates them a
        session and returns the authenticated user and token.

        :param username: The users username
        :param password: The users password
        :param remote_address: Remote address of the client
        :param user_agent: User agent of the client
        :return: Authenticated user, JWT token
        """

        user = authenticate(username=username, password=password)

        if user is None or not user.is_active:
            logger.info('Authentication failed', username=username)
            raise AuthenticationError('Authentication failed')

        return cls.objects.create_session(user, remote_address, user_agent, **kwargs)


    @classmethod
    def validate_token(cls, token):
        """
        Authenticates the given JWT token

        :param token: JWT Token provided by the user
        :return: Authenticated user
        """
        token_data = cls.objects.decode_token(token)
        if token_data is None:
            logger.info('Authentication failed')
            raise AuthenticationError('Authentication failed')

        return token_data


    @classmethod
    def authenticate_token(cls, token):
        """
        Authenticates a user with a given token

        :param token: JWT Token provided by the user
        :return: Authenticated user
        """
        token_data = cls.objects.decode_token(token)
        if token_data is None:
            logger.info('Authentication failed')
            raise AuthenticationError('Authentication failed')

        try:
            api_session = cls.objects.get(
                pk=token_data['session_id'],
                user__pk=token_data['user_id'],
                user__is_active=True,
                is_active=True,
            )
        except cls.DoesNotExist:
            logger.info('Authentication failed', session_id=token_data['session_id'])
            raise AuthenticationError('Authentication failed')

        try:
            cls.objects.log_session_access(api_session)
        except SessionExpiredError:
            logger.info('Authentication failed', session_id=api_session.id)
            raise AuthenticationError('Authentication failed')

        logger.info('User auth successful', user_id=api_session.user.id)
        return api_session, token_data

    @classmethod
    def logout_user(cls, token):
        """
        :param token: JWT Token provided by the user
        :return: None
        """

        token_data = cls.objects.decode_token(token)
        cls.objects.deactivate_session(token_data['session_id'])
        logger.info('User logged out', user_id=token_data['user_id'])


class APISessionAccess(models.Model):
    """API Session Access"""

    session = models.ForeignKey(
        APISession, on_delete=models.CASCADE, related_name="accesses")
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "API session access"
        verbose_name_plural = "API session accesses"
        app_label = "rest_sessions"
        ordering = ["-created"]
        get_latest_by = ["created"]
