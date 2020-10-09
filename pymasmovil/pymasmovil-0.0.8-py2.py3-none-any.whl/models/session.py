from pymasmovil.client import Client
from pymasmovil.errors.exceptions import MissingLoginCredentialsError, AutenthicationError
import os


class Session():

    def __init__(self, session_id):
        self.session_id = session_id

    @classmethod
    def create(cls):

        route = '/v0/login-api'

        login_params = (
            ('username', os.getenv('MM_USER')),
            ('password', os.getenv('MM_PASSWORD')),
            ('domain', os.getenv('MM_DOMAIN')),
        )

        if login_params[0][1] is None:
            raise MissingLoginCredentialsError('MM_USER')
        elif login_params[1][1] is None:
            raise MissingLoginCredentialsError('MM_PASSWORD')
        elif login_params[2][1] is None:
            raise MissingLoginCredentialsError('MM_DOMAIN')

        session = Client().post(route=route, params=login_params, body={})

        if not session["sessionId"]:
            raise AutenthicationError

        return Session(session["sessionId"])
