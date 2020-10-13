from .context import *
from .entities import *
from .loader import *
from .queries import *
from .services import *
from .transactions import *


class Environments:

    @property
    def dev(self):
        return Environment('https://dev.kladama.com')

    @property
    def local(self):
        return Environment('http://localhost')

    @property
    def prod(self):
        return Environment('https://kladama.com')

    @property
    def sandbox(self):
        return Environment('https://sandbox.kladama.com')


def authenticate(env, api_token):
    return Session(env, api_token)
