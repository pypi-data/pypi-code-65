# Constants

import logging

DEFAULT_PORT = 7777
DEFAULT_IP = '127.0.0.1'
MAX_CONNECT = 5
MAX_PACKAGE_LEN = 1024
ENCODING = 'utf-8'

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
RECIPIENT = 'to'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
PUBLIC_KEY_REQUEST = 'pubkey_need'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

LOGGING_LEVEL = logging.DEBUG
TERMINALS_TO_LAUNCH = ('Dima', 'Oleg', 'Lena')
SERVER_CONFIG = 'server.ini'