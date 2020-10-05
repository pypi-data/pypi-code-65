from pycoingecko import CoinGeckoAPI
from requests.exceptions import HTTPError

from .. import AlgoLabAPI
from ...tradables import AlgoLabTradable, AlgoLabCryptoTradable


TRADABLE_TABLE = {
    AlgoLabCryptoTradable.BTC: "bitcoin",
    AlgoLabCryptoTradable.BSV: "bitcoin-cash-sv",
    AlgoLabCryptoTradable.LTC: "litecoin",
    AlgoLabCryptoTradable.ETH: "ethereum",
}


class AlgoLabCoinGeckoAPI(AlgoLabAPI):
    def __init__(self):
        self._api = CoinGeckoAPI()

    def up(self) -> bool:
        """
        returns true or false if service is up
        """
        try:
            self._api.ping()['gecko_says']
            return True
        except (KeyError, HTTPError):
            return False

    def get_price(self, tradable: AlgoLabCryptoTradable, currency: str = 'usd') -> tuple:
        """
        get the current price of tradable in `currency`
        returns a tuple of (last_updated, current_price)
        """
        coin_data = self._api.get_coin_by_id(id=TRADABLE_TABLE[tradable])
        last_updated = coin_data['last_updated']
        current_price = coin_data['market_data']['current_price'][currency]
        return (last_updated, current_price)
