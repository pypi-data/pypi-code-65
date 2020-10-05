from ..apis import AlgoLabAPI
from ..tradables import AlgoLabTradable


class AlgoLabPriceListener():
    def __init__(self, api: AlgoLabAPI, tradable: AlgoLabTradable, callback: callable, update_frequency=None):
        self._current_data = None
        self._last_updated = None
        self._history = []

        self._update_frequency = update_frequency
        self._api = api
        self._tradable = tradable
        self._callback = callback

    def _change(self):
        """
        passes callback the data.
        data is (timestamp, price)
        """
        self._callback(self._current_data)

    def _update(self):
        """
        The listener manages the update behavior for
        user extensibility. Timing the call of this event
        is the scope of the service
        """
        last_updated, data = self._api.get_price(self._tradable)
        if not self._last_updated \
                or not self._current_data \
                or self._last_updated > last_updated:
            self._last_updated = last_updated
            self._current_data = (last_updated, data)
            self._change()
