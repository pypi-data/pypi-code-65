from threading import Thread

from .abc_algo import AlgoLabAlgorithm
from .apis.consumer import AlgoLabConsumerAPI
from .price_listener.service import AlgoLabPriceListenerService


class AlgoLabService():
    def __init__(self):
        """
        The whole service
        It runs shit
        """
        self._listener_service = AlgoLabPriceListenerService()
        self._consumer_api = AlgoLabConsumerAPI(self._listener_service)
        self._running = False
        self._running_algos = []
        self._thread = Thread(target=self._thread_loop)

    def _start(self):
        """
        start a new thread for work
        """
        self._running = True
        self._listener_service._start()
        self._thread.start()

    def _stop(self, timeout=None):
        """
        stop the listening thread
        """
        for algo in self._running_algos:
            algo.__destroy__()

        self._running = False
        self._listener_service._stop(timeout=timeout)
        self._thread.join(timeout=timeout)

    def _thread_loop(self):
        while self._running:
            pass

    def _run_algo(self, algo: AlgoLabAlgorithm):
        self._running_algos.append(algo(self._consumer_api))
