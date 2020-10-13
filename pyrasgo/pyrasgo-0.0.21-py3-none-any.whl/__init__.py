__all__ = [
    'connect',
]

from pyrasgo.api import RasgoConnection

def connect(api_key):
    conn = RasgoConnection(api_key=api_key)
    return conn