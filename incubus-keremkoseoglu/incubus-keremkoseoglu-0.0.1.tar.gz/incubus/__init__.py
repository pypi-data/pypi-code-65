""" Main functionality """
from threading import Thread
from time import sleep
import os


__version__ = "0.0.1"
AUTHOR = "Kerem Koseoglu"
EMAIL = "kerem@keremkoseoglu.com"
DESCRIPTION = "Idle app killer"
PYTHON_VERSION = ">=3.6.5"


class Incubus:
    """ Main class """
    def __init__(self):
        self._idle_min_limit = 0
        self._min_ticks = 0

    def start(self, idle_min_limit: int):
        """ Starts the functionality """
        self._idle_min_limit = idle_min_limit
        self._min_ticks = 0
        Thread(target=self._start, daemon=True).start()

    def user_event(self):
        self._min_ticks = 0

    def _start(self):
        while True:
            self._min_ticks += 1
            if self._min_ticks > self._idle_min_limit:
                os._exit(0) # pylint: disable=W0212
            sleep(60)


class IncubusFactory:
    """ Singleton logic """
    _SINGLETON: Incubus = None

    @staticmethod
    def get_instance() -> Incubus:
        if IncubusFactory._SINGLETON is None:
            IncubusFactory._SINGLETON = Incubus()
        return IncubusFactory._SINGLETON
