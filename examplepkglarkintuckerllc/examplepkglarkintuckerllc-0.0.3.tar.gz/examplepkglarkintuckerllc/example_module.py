"""Provide an example module."""
from random_word import RandomWords


r = RandomWords()


def hello():
    """Return greeting."""
    return 'Hello World!'


def random():
    """Return random word."""
    random = r.get_random_word()
    return random
