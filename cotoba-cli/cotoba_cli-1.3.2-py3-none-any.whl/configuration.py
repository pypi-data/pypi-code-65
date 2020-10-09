import base64
import click
import os
import toml

import boto3
from jose import jwt
from datetime import datetime
from logging import config as logging_config

CONFIG_DIRECTORY_NAME = '.cotoba'
LOGFILE_NAME = 'cotoba-cli.log'


def config_directory():
    """
    returns config directry.
    if not directory exists, make directory.

    Returns
    -------
    directory: str
      config directory
    """
    default_directory = os.path.join(os.path.expanduser('~'), CONFIG_DIRECTORY_NAME)
    directory = os.environ.get('COTOBA_HOME', default_directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


class BaseConfiguration(object):
    """
    Singleton base class to handle configuration file.
    """

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, '_instance'):
            instance = super(BaseConfiguration, cls).__new__(cls)
            home_dir = config_directory()
            cls._config_filepath = os.path.join(home_dir, instance.config_filename)
            if not os.path.exists(cls._config_filepath):
                with open(cls._config_filepath, 'w') as f:
                    toml.dump(instance.default_config, f)

            instance.load_config()
            cls._instance = instance

        return cls._instance

    @property
    def config(self):
        return self._config

    @property
    def config_filepath(self):
        return self._config_filepath

    @property
    def config_filename(self):
        raise NotImplementedError()

    @property
    def default_config(self):
        raise NotImplementedError()

    def load_config(self):
        with open(self._config_filepath, 'r') as f:
            self._config = toml.load(f)

    def save_config(self):
        with open(self._config_filepath, 'w') as f:
            toml.dump(self._config, f)


class Configuration(BaseConfiguration):
    DEFAULT_AUTH = 'YXAtbm9ydGhlYXN0LTFfNVMweWt0cFpxLDQ2aHB0MGhhcm5ha2N1YnN0czlzcTR1NXQz'

    @property
    def config_filename(self):
        return 'config.toml'

    @property
    def default_config(self):
        return {
            'default': {
                'endpoint-url': 'https://api.cotoba.net/',
                'locale': 'ja-JP'
            }
        }

    @property
    def endpoint_url(self):
        return self._config['default']['endpoint-url']

    @endpoint_url.setter
    def endpoint_url(self, v):
        self._config['default']['endpoint-url'] = v

    @property
    def locale(self):
        return self._config['default']['locale']

    @locale.setter
    def locale(self, v):
        self._config['default']['locale'] = v

    @property
    def authorization(self):
        # if authorization is not set, returns default auth value
        # this process hides default auth value from production users.
        return self._config['default'].get('authorization', self.DEFAULT_AUTH)

    @authorization.setter
    def authorization(self, v):
        self._config['default']['authorization'] = v

    def _decode_authorization(self):
        """
        Returns:
          [pool id, client id]
        """
        auth_bytes = self.authorization.encode('ascii')

        try:
            decodeded_auth = base64.decodebytes(auth_bytes).decode('ascii')
        except base64.binascii.Error:
            raise click.ClickException('Authorization id is invalid format.')

        if decodeded_auth.count(',') != 1:
            raise click.ClickException('Authorization id is invalid.')

        return decodeded_auth.strip().split(',')

    @property
    def pool_id(self):
        return self._decode_authorization()[0]

    @property
    def client_id(self):
        return self._decode_authorization()[1]


class Session(BaseConfiguration):
    @property
    def config_filename(self):
        return 'session.toml'

    @property
    def default_config(self):
        return {
            'default': {
                'id': '',
                'id_token': '',
                'access_token': '',
                'refresh_token': '',
            }
        }

    @property
    def id(self):
        if not self._config['default']['id']:
            raise click.ClickException('You are not logged in.')
        return self._config['default']['id']

    @id.setter
    def id(self, v):
        self._config['default']['id'] = v

    @property
    def id_token(self):
        if not self._config['default']['id_token']:
            raise click.ClickException('You are not logged in.')
        self.renew_token_if_expired()
        return self._config['default']['id_token']

    @id_token.setter
    def id_token(self, v):
        self._config['default']['id_token'] = v

    @property
    def access_token(self):
        if not self._config['default']['access_token']:
            raise click.ClickException('You are not logged in.')
        self.renew_token_if_expired()
        return self._config['default']['access_token']

    @access_token.setter
    def access_token(self, v):
        self._config['default']['access_token'] = v

    @property
    def refresh_token(self):
        if not self._config['default']['refresh_token']:
            raise click.ClickException('You are not logged in.')
        return self._config['default']['refresh_token']

    @refresh_token.setter
    def refresh_token(self, v):
        self._config['default']['refresh_token'] = v

    @property
    def sub(self):
        decoded_access_token = jwt.get_unverified_claims(self.access_token)
        return decoded_access_token['sub']

    def renew_token_if_expired(self):
        now = datetime.now()
        token = self._config['default']['access_token']
        decoded_access_token = jwt.get_unverified_claims(token)

        if now > datetime.fromtimestamp(decoded_access_token['exp']):
            self.renew_token_using_refresh_token()

    def renew_token_using_refresh_token(self):
        client = boto3.client(
            'cognito-idp',
            region_name='ap-northeast-1',
            aws_access_key_id='dummy',
            aws_secret_access_key='dummy')
        response = client.initiate_auth(
            AuthFlow='REFRESH_TOKEN',
            AuthParameters={'REFRESH_TOKEN': self.refresh_token},
            ClientId=Configuration().client_id)
        self.id_token = response['AuthenticationResult']['IdToken']
        self.access_token = response['AuthenticationResult']['AccessToken']
        self.save_config()


def logfile_path():
    directory = config_directory()
    logfile_path = os.path.join(directory, LOGFILE_NAME)
    return logfile_path


def initialize_logger():
    logging_config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'formatter': {
                'format': '[%(levelname)s] %(asctime)s %(pathname)s(%(lineno)s): %(message)s'
            }
        },
        'handlers': {
            'file_handler': {
                'level': 'INFO',
                'formatter': 'formatter',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': logfile_path(),
                'maxBytes': 1000000,
                'backupCount': 3,
                'encoding': 'utf-8',
            },
            'console_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'formatter',
                'level': 'WARN',
            }
        },
        'root': {
            'handlers': ['file_handler', 'console_handler'],
        }
    })
