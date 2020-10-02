import keyring
import os

class KeyringFetch(object):
    """Functions for converting between vendor tickers and findatapy tickers (and vice-versa).

    """

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def key_store(service_name):
        key = None

        # This will fail on some cloud notebook platforms so put in try/except loop
        try:
            key = keyring.get_password(service_name, os.getlogin())
        except:
            pass

        return key