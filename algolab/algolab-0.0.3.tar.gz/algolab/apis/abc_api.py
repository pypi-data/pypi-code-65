from abc import ABC, abstractclassmethod
from ..tradables import AlgoLabTradable


class AlgoLabAPI(ABC):
    @abstractclassmethod
    def get_price(self, tradable: AlgoLabTradable, currency: str = 'usd'):
        """
        get the current price in `currency`
        """
        pass

    @abstractclassmethod
    def up(self) -> bool:
        """
        returns true or false if service is up
        """
        pass
