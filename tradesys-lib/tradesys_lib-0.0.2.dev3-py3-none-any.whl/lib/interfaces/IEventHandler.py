from abc import ABC, abstractmethod
from ..types import Symbol, TradeTransaction, AccountBalance


class IEventHandlers(ABC):
    """
    Base class for all streaming client's event handlers. The child classes choose which methods to implement
    depending on the requirements.
    """
    @abstractmethod
    def on_price_update(self, data: dict) -> Symbol:
        pass

    @abstractmethod
    def on_trade_update(self, data: dict) -> TradeTransaction:
        pass

    @abstractmethod
    def on_balance_update(self, data: dict) -> AccountBalance:
        pass

    @abstractmethod
    def on_trade_status_update(self, data: dict) -> TradeTransaction:
        pass

    @abstractmethod
    def on_profit_update(self, data: dict) -> None:
        pass

    @abstractmethod
    def on_news_update(self, data: dict) -> None:
        pass

    @abstractmethod
    def on_candle_update(self, data: dict) -> Symbol:
        pass

    @abstractmethod
    def on_unhandled_update(self, data: dict):
        pass
