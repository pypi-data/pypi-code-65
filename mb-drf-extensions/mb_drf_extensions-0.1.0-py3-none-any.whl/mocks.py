import json
import uuid

from requests_mock import Mocker

from .authentication import OAuth2Mixin


class AuthenticationMock(Mocker):
    def __init__(
            self,
            username,
            user_uuid=None,
            user_scope=None,
            access_token=None,
    ):
        super().__init__()
        self.username = username
        self.user_uuid = user_uuid or uuid.uuid4().hex
        self.user_scope = (
            ' '.join(user_scope) if
            isinstance(user_scope, (list, tuple)) else ''
        )
        self.access_token = access_token or uuid.uuid4().hex

    def start(self):
        super().start()
        self.register_uri(
            'POST', OAuth2Mixin.oauth2_login_url,
            text=json.dumps({
                'access_token': self.access_token,
                'expires_in': 36000
            }),
        )
        self.register_uri(
            'POST', OAuth2Mixin.oauth2_introspect_url,
            text=json.dumps({
                'scope': self.user_scope,
                'user': {
                    'username': self.username,
                    'uuid': self.user_uuid,
                }
            }),
        )
