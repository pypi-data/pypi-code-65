import logging
import datetime
import jwt

from django.db import models
from django.conf import settings
from django.utils import module_loading, timezone
from ua_parser import user_agent_parser

from restless_dj_utils.rest_sessions.conf import ACCESS_BACKEND, INACTIVITY_TIMEOUT


logger = logging.getLogger(__name__)


def _load_settings():
    for setting in settings.AUTH_JWT_SECRET_KEYS.split(','):
        yield setting.split(':')


def _get_backend():
    return module_loading.import_string(ACCESS_BACKEND)()


class APISessionManager(models.Manager):
    """Auth service object"""

    def get_inactivity_timeout(self, api_session):
        return INACTIVITY_TIMEOUT

    def generate_token_data(self, user, **kwargs):
        return {}

    def get_last_access(self, api_session):
        backend = _get_backend()
        return backend.get_last_access(api_session)

    def get_expires(self, api_session):
        inactivity_timeout = self.get_inactivity_timeout(api_session)
        last_access = self.get_last_access(api_session)
        return last_access + datetime.timedelta(seconds=inactivity_timeout)

    def has_expired(self, api_session):
        return self.get_expires(api_session) < timezone.now()

    def log_session_access(self, api_session, is_new=False):
        inactivity_timeout = self.get_inactivity_timeout(api_session)
        backend = _get_backend()
        return backend.log_session_access(api_session, inactivity_timeout, is_new)

    def create_session(self, user, remote_address, user_agent, **kwargs):
        """
        Authenticates a user with django authenticate method, creates them a
        session and returns the authenticated user and token.

        :param username: The users username
        :param password: The users password
        :param remote_address: Remote address of the client
        :param user_agent: User agent of the client
        :return: Authenticated user, JWT token
        """

        token_data = self.generate_token_data(user, **kwargs)
        description = kwargs.pop('description', 'API session')

        agent_data = user_agent_parser.Parse(user_agent)
        api_session = self.get_queryset().create(
            user=user, remote_address=remote_address, user_agent=agent_data,
            description=description, token_data=token_data)

        token = self.encode_token(api_session.get_token_data()).decode('utf-8')
        self.log_session_access(api_session, is_new=True)
        return api_session, token

    def deactivate_session(self, api_session_id):
        self.get_queryset().filter(pk=api_session_id).update(is_active=False)

    def encode_token(self, token_data):
        algorithm, key = next(_load_settings())
        return jwt.encode(token_data, key, algorithm=algorithm)

    def decode_token(self, token):
        for algorithm, key in _load_settings():
            try:
                return jwt.decode(token, key, algorithms=[algorithm])
            except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
                pass
