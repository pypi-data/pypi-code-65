from typing import Union
from datetime import datetime
from . import constants


class User(object):
    def __init__(self, currency: str = "USD", group: Union[str, None] = None, leverage: float = 0.0,
                 trailing_stop_enabled: bool = False):
        self.currency = currency
        self.group = group
        self.leverage_multiplier = leverage
        self.trailing_stop = trailing_stop_enabled


class Commission(object):
    def __init__(self, commission: float = 0.0, exchange_rate: Union[None, float] = None):
        self.commission = commission
        self.exchange_rate = exchange_rate

    @property
    def exchange_value(self) -> float:
        if self.exchange_rate is not None:
            return self.commission * self.exchange_rate
        return self.commission

    def __repr__(self) -> str:
        return f"Commission {self.commission} at exchange rate of {self.exchange_rate}, yields {self.exchange_value}"


class AccountBalance(object):
    def __init__(self, balance: float = 0.0, credit: float = 0.0, currency: str = "USD", equity: float = 0.0,
                 margin: float = 0.0, free_margin: float = 0.0):
        self.balance = balance
        self.credit = credit
        self.currency = currency
        self.equity = equity
        self.margin = margin
        self.free_margin = free_margin

    @property
    def margin_level(self):
        if self.margin == 0.0:
            return 0.0

        return 100 * (self.equity / self.margin)

    def __repr__(self):
        return f"Account balance of {self.balance} {self.currency}.\nTotal equity: {self.equity} {self.currency}.\nMargin level: {self.margin_level}%."



class TimeStamp:
    def __init__(self, time_value: Union[str, int, float], unix: bool = False, milliseconds: bool = False):
        self.unix_time = None
        self.time_format = "%d-%m-%Y %H:%M:%S UTC"
        if unix:
            if milliseconds:
                self.unix_time = time_value / 1000.00
            else:
                self.unix_time = time_value
        else:
            raise NotImplementedError("Currently only accepts unix timestamps.")

    def __repr__(self):
        return datetime.utcfromtimestamp(float(self.unix_time)).strftime(self.time_format)


class Symbol(object):
    def __init__(self, ticker: str = "", ask: float = 0.0, bid: float = 0.0, category: str = "CFD",
                 contract_size: float = 0.0, currency: str = "USD", currency_pair: bool = False,
                 currency_profit: str = "USD", description: Union[None, str] = None,
                 expiration: Union[None, TimeStamp] = None, high: float = 0.0, initial_margin: float = 0.0,
                 leverage: float = 0.0, long_only: bool = False, min_lot: float = 0.0, max_lot: float = 0.0,
                 lot_step: float = 0.0, low: float = 0.0, pip_precision: int = 1, price_precision: int = 1,
                 shortable: bool = False, time: Union[None, TimeStamp] = None):

        self.ticker = ticker
        self.ask = ask
        self.bid = bid
        self.category = category
        self.contract_size = contract_size
        self.currency = currency
        self.currency_pair = currency_pair
        self.currency_profit = currency_profit
        self.description = description
        self.expiration = expiration
        self.high = high
        self.initial_margin = initial_margin
        self.leverage = leverage
        self.long_only = long_only
        self.lot_min = min_lot
        self.lot_max = max_lot
        self.lot_step = lot_step
        self.low = low
        self.pip_precision = pip_precision
        self.price_precision = price_precision
        self.shortable = shortable

        if time is None:
            self.time = TimeStamp(float(datetime.utcnow().timestamp()), unix=True)
        else:
            self.time = time

    def __repr__(self):
        return f"Symbol(symbol={self.ticker}, ask={self.ask}, bid={self.bid}, spread={abs(self.ask - self.bid)}, currency={self.currency}, " \
               f"time='{self.time}')"


class TradeTransaction(object):
    def __init__(self, symbol: Symbol, operation: int = constants.TransactionSide.BUY_LIMIT, comment: str = "",
                 expiration: int = 0, trailing_offset: int = 0, order: int = 0, price: float = 0.0,
                 stop_loss: float = 0.0, take_profit: float = 0.0, volume: float = 0.1,
                 transaction_type: int = constants.TransactionType.ORDER_OPEN
                 ):
        self.operation = operation
        self.comment = comment
        self.expiration = expiration
        self.trailing_offset = trailing_offset
        self.order_number = order
        self.price = price
        self.stop_loss_price = stop_loss
        self.symbol = symbol
        self.take_profit_price = take_profit
        self.transaction_type = transaction_type
        self.volume = volume

    def __repr__(self):
        return str(self.__dict__)


class Credentials(object):
    """Credentials can either be TOKEN or PASSWORD. In the case a credential is a TOKEN, the value of username will be
    set to both the username and password field for compatibility reasons. """

    def __init__(self, username: Union[str, int], password: Union[None, str] = None, is_token: bool = False):
        self.username = username
        self.password = password
        self.is_token = is_token

        if is_token:
            self.password = username

        if type(username) not in (str, int):
            raise TypeError("Parameter username must be either a string or an integer.")

    def __repr__(self):
        if self.is_token:
            return "TOKEN credential object."

        return f"Password credential object for user {self.username}."


