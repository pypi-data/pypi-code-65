import boto3
import click
import logging
import botocore

from cotoba_cli import session
from cotoba_cli import config
from cotoba_cli import platform
from datetime import datetime
from jose import jwt

USER_POOL_REGION = 'ap-northeast-1'

logger = logging.getLogger(__name__)
aws_config = botocore.config.Config(signature_version=botocore.UNSIGNED)
client = boto3.client('cognito-idp',
                      region_name=USER_POOL_REGION,
                      config=aws_config)


class Authorization:
    def __init__(self, id_token, access_token, refresh_token, sub, client_id):
        self.id_token = id_token
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.sub = sub
        self.client_id = client_id

    def renew_token_if_expired(self):
        if not self.access_token:
            raise click.ClickException("You are not logged in. Run 'cotoba login' to login.")
        now = datetime.now()
        decoded_access_token = jwt.get_unverified_claims(self.access_token)

        if now > datetime.fromtimestamp(decoded_access_token['exp']):
            self.renew_access_token_using_refresh_token()
            decoded_access_token = jwt.get_unverified_claims(self.access_token)
        self.sub = decoded_access_token['sub']

    def renew_access_token_using_refresh_token(self):
        response = client.initiate_auth(
            AuthFlow='REFRESH_TOKEN',
            AuthParameters={
                'REFRESH_TOKEN': self.refresh_token,
            },
            ClientId=self.client_id
        )
        self.id_token = response['AuthenticationResult']['IdToken']
        self.access_token = response['AuthenticationResult']['AccessToken']


def get_cognito_authorization():
    session_dict = session.load()['default']
    if 'id_token' not in session_dict \
       or 'refresh_token' not in session_dict \
       or 'access_token' not in session_dict:
        raise click.ClickException("You are not logged in. Run 'cotoba login' to login.")

    config_dict = config.load()['default']
    if 'authorization' not in config_dict:
        raise click.ClickException('Authorization id is not set')
    authorization = config_dict['authorization']
    user_pool_id, client_id = platform.decode_cognito_setting(
        authorization)

    auth = Authorization(id_token=session_dict['id_token'],
                         access_token=session_dict['access_token'],
                         refresh_token=session_dict['refresh_token'],
                         sub=None,
                         client_id=client_id)
    auth.renew_token_if_expired()

    if auth.access_token != session_dict['access_token']:
        session.save(
            login_id=None,
            id_token=auth.id_token,
            refresh_token=auth.refresh_token,
            access_token=auth.access_token)

    return auth
