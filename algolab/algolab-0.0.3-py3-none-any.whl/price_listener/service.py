from threading import Thread
import time
from uuid import uuid4, UUID

from .listener import AlgoLabPriceListener


class AlgoLabPriceListenerService():
    def __init__(self):
        self._listeners: {UUID} = {}
        self._thread = Thread(target=self._thread_loop)
        self._running = False

    def _start(self):
        """
        start a new thread for listening
        """
        self._running = True
        self._thread.start()

    def _stop(self, timeout=None):
        """
        stop the listening thread
        """
        self._running = False
        self._thread.join(timeout=timeout)

    def _thread_loop(self):
        while self._running:
            for key in list(self._listeners):
                self._listeners[key]._update()
                time.sleep(1)

    def register(self, listener: AlgoLabPriceListener) -> UUID:
        """
        returns UUID of item to be able to deregister later
        """
        uuid = uuid4()
        self._listeners[uuid] = listener
        # The listener manages its own API, so that a
        # user may extend the behavior, we just
        # manage the update frequency for resource
        # util management
        listener._update()
        return uuid

    def deregister(self, uuid: UUID):
        """
        deregister listener from service

        args:
            uuid: the uuid returned when registering the listener
        """
        del self._listeners[uuid]
