from abc import ABC, abstractmethod
from typing import Union, List, Tuple
import difflib
from ..interfaces.IEventHandler import IEventHandlers
from ..types import Symbol, Commission, User, AccountBalance, TimeStamp, TradeTransaction, Credentials


class IBroker(ABC):
    client = None
    authenticated = False

    @abstractmethod
    def connect(self, user: Union[str, int] = "", password: str = None) -> bool:
        """
        Logs in and establishes a connection to the API. Required for any other operation to complete.

        Args:
            user: Username to use for login.
            password: Password or token to use in conjunction to the user.

        Returns:
            A boolean indicating success (True) or failure (False)
        """
        pass

    @abstractmethod
    def connect_with_credentials(self, credentials: Credentials) -> bool:
        """
        Uses credentials from a credential loader that inherited from
        tradesys.lib.interfaces.ILoader. Implementation of how the credentials
        are parsed are specific to their manager.

        Args:
            credentials: A tradesys.lib.types.Credentials object returned from a credential loader.

        Returns:
            A boolean indicating success (True) or failure (False)
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Cleanly shuts down the API connection.

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_symbol(self, symbol: Union[str, Symbol]) -> Symbol:
        """
        Attempts to fetch the provided Symbol from the broker.

        Args:
            symbol: An str or tradesys.lib.types.Symbol object specifying the desired symbol.

        Returns:
            An updated tradesys.lib.types.Symbol object with the latest data.
        """
        pass

    def search_symbol(self, symbol: str) -> Union[None, Symbol]:
        """
        Searches for the correct ticker of a Symbol, given a close enough match.

        **This is an expensive operation. Do no overuse.**

        Args:
            symbol: A string denoting the part of the symbol to search for.

        Returns:
            A tradesys.lib.types.Symbol object if a match was found or None, if no match was found.

        """
        all_symbols = self.get_available_symbols()
        all_symbols_str = [sym.ticker for sym in all_symbols]
        matches = difflib.get_close_matches(symbol, all_symbols_str, 3)
        if len(matches) == 1:
            return self.get_symbol(str(matches[0]))
        else:
            print(f"Closest matches: {matches}")

        return None

    @abstractmethod
    def get_available_symbols(self) -> List[Symbol]:
        """
        Broker specific implementation to get a list of available symbols under the connected account.

        Returns:
            A list of tradesys.lib.types.Symbol objects.
        """
        pass

    @abstractmethod
    def get_commission(self, volume: float, symbol: Union[str, Symbol]) -> Commission:
        """
        Returns the commission to be paid for trading the specified volume on the specified symbol, given the
        current market environment.

        Args:
            volume: A float indicating the volume to be traded.
            symbol: A string or a tradesys.lib.types.Symbol indicating the instrument to be traded.

        Returns:
            Commission information contained in a tradesys.lib.types.Commission object.
        """
        pass

    @abstractmethod
    def get_current_user_data(self) -> User:
        pass

    @abstractmethod
    def get_account_balance(self) -> AccountBalance:
        """
        Gets the current user account balance.

        Returns:
            The current user account balance and basic information encapsulated in a tradesys.lib.types.AccountBalance object.
        """
        pass

    @abstractmethod
    def get_server_time(self) -> TimeStamp:
        """
        Gets the connected server time.

        Returns:
            A tradesys.lib.types.TimeStamp object denoting the server time.
        """
        # Returns unix timestamp of server time
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        Gets the API Version, if available

        Returns:
            A string denoting the API version connected to.
        """
        pass

    @abstractmethod
    def connection_status(self) -> bool:
        """
        Checks if the connection is still alive and ready for commands.

        Returns:
            A boolean indicating the connection status.
        """
        pass

    @abstractmethod
    def check_transaction_status(self, transaction: TradeTransaction) -> bool:
        pass

    @abstractmethod
    def open_position(self, transaction: TradeTransaction) -> TradeTransaction:
        pass


class IStreamingBroker(ABC):

    @abstractmethod
    def set_handler(self, new_handler: IEventHandlers):
        pass

    @abstractmethod
    def subscribePrice(self, symbol):
        pass

    @abstractmethod
    def subscribePrices(self, symbols):
        pass

    @abstractmethod
    def subscribeTrades(self):
        pass

    @abstractmethod
    def subscribeBalance(self):
        pass

    @abstractmethod
    def subscribeTradeStatus(self):
        pass

    @abstractmethod
    def subscribeProfits(self):
        pass

    @abstractmethod
    def subscribeNews(self):
        pass

    @abstractmethod
    def unsubscribePrice(self, symbol):
        pass

    @abstractmethod
    def unsubscribePrices(self, symbols):
        pass

    @abstractmethod
    def unsubscribeTrades(self):
        pass

    @abstractmethod
    def unsubscribeBalance(self):
        pass

    @abstractmethod
    def unsubscribeTradeStatus(self):
        pass

    @abstractmethod
    def unsubscribeProfits(self):
        pass

    @abstractmethod
    def unsubscribeNews(self):
        pass
