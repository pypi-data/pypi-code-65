from random import choice
from string import ascii_uppercase, digits
import requests

DOMAINS = [
    'getnada.com',
    'amail.club',
    'banit.club',
    'cars2.club',
    'cmail.club',
    'banit.me',
    'duck2.club',
    'nada.email',
    'nada.ltd',
    'wmail.club'
]

GET_INBOX = 'https://getnada.com/api/v1/inboxes/{}'
GET_MESSAGE = 'https://getnada.com/api/v1/messages/{}'


class EmailResult:
    def __init__(self, guid: str, subject: str, sender: str, datetime: str, body: str = None):
        self.body = body
        self.datetime = datetime
        self.sender = sender
        self.subject = subject
        self.guid = guid


class Nada:
    def __init__(self, name=None, domain=None):
        self.name = (name or Nada.id_generator()).lower()
        self.domain = domain or choice(DOMAINS)

    def __str__(self):
        return '{}@{}'.format(self.name, self.domain)

    def get_email_list(self):
        result = []
        try:
            response = requests.get(GET_INBOX.format(self))
            data = response.json()['msgs']
            result = [EmailResult(x['uid'], x['s'], x['fe'], x['rf']) for x in data]
        except Exception:
            pass

        return result

    @staticmethod
    def get_email(uid):
        result: EmailResult = None
        try:
            response = requests.get(GET_MESSAGE.format(uid))
            data = response.json()  # [ru, d, f, text, fe, html, s, response, at, rf, ib, uid]
            result = EmailResult(data['uid'], data['s'], data['fe'], data['rf'], data['text'] or data['html'])
        except Exception:
            pass
        return result

    @staticmethod
    def id_generator(size=6, chars=ascii_uppercase + digits):
        return ''.join(choice(chars) for _ in range(size))
