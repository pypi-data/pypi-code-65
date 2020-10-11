""" Vibhaga initialization module """
from os import path
from sys import modules

def get_root_path() -> str:
    """ Returns the root path of Vibhaga """
    return path.dirname(modules['__main__'].__file__)
