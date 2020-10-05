from ...price_listener.service import AlgoLabPriceListenerService


class AlgoLabConsumerAPI():
    def __init__(self, listener_service: AlgoLabPriceListenerService):
        """
        docstring
        """
        self._listener_service = listener_service

    def get_listener_service(self) -> AlgoLabPriceListenerService:
        return self._listener_service
