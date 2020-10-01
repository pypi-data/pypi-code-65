from typing import Tuple, Union, List
import socket
import ssl
import json
import time
from threading import Thread
from ..interfaces.IBroker import IBroker, IStreamingBroker
from ..interfaces.IEventHandler import IEventHandlers
from ..types import TradeTransaction, TimeStamp, AccountBalance, User, Symbol, Commission, Credentials


class DefaultEventHandler(IEventHandlers):

    def on_price_update(self, data: dict) -> None:
        print(data)

    def on_trade_update(self, data: dict) -> None:
        print(data)

    def on_balance_update(self, data: dict) -> None:
        print(data)

    def on_trade_status_update(self, data: dict) -> None:
        print(data)

    def on_profit_update(self, data: dict) -> None:
        print(data)

    def on_news_update(self, data: dict) -> None:
        print(data)

    def on_candle_update(self, data: dict) -> None:
        print(data)

    def on_unhandled_update(self, data: dict) -> None:
        print(data)


class XTBStreamingClient(IStreamingBroker):

    def __init__(self, streaming_session: str, event_handlers: Union[None, IEventHandlers] = None, address: str = 'xapi.xtb.com', port: int = 5125, encrypt=True):
        # Socket parameters
        self._maxConnectionRetries = 3
        self._apiTimeout = 100

        self._ssl = encrypt
        if not self._ssl:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket = ssl.wrap_socket(sock)
        self.conn = self.socket
        self._timeout = None
        self._address = address
        self._port = port
        self._decoder = json.JSONDecoder()
        self._receivedData = ''

        # XTB Params
        self._ssId = streaming_session
        if event_handlers is None:
            self.event_handlers = DefaultEventHandler()
        else:
            self.event_handlers = event_handlers

        if not self.connect():
            raise Exception("Cannot connect to streaming on " + address + ":" + str(port) + " after " + str(
                self._maxConnectionRetries) + " retries")

        self._running = True
        self._t = Thread(target=self._readStream, args=())
        self._t.setDaemon(True)
        self._t.start()

    def connect(self):
        for i in range(self._maxConnectionRetries):
            try:
                self.socket.connect((self._address, self._port))
            except socket.error as msg:
                time.sleep(0.25)
                continue
            return True
        return False

    def _sendObj(self, obj: dict):
        msg = json.dumps(obj)
        self._waitingSend(msg)

    def _waitingSend(self, msg: str):
        if self.socket:
            sent = 0
            msg = msg.encode('utf-8')
            while sent < len(msg):
                sent += self.conn.send(msg[sent:])
                time.sleep(self._apiTimeout / 1000)

    def _read(self, bytes_size: int = 4096):
        if not self.socket:
            raise RuntimeError("socket connection broken")
        resp = None
        while True:
            char = self.conn.recv(bytes_size).decode()
            self._receivedData += char
            try:
                (resp, size) = self._decoder.raw_decode(self._receivedData)
                if size == len(self._receivedData):
                    self._receivedData = ''
                    break
                elif size < len(self._receivedData):
                    self._receivedData = self._receivedData[size:].strip()
                    break
            except ValueError as e:
                continue
        return resp

    def _readObj(self):
        msg = self._read()
        return msg

    def close(self):
        self._closeSocket()
        if self.socket is not self.conn:
            self._closeConnection()

    def _closeSocket(self):
        self.socket.close()

    def _closeConnection(self):
        self.conn.close()

    # XTB streaming stuff
    def disconnect(self):
        self._running = False
        self._t.join()
        self.close()

    def execute(self, dictionary: dict):
        self._sendObj(dictionary)

    def _readStream(self):
        while self._running:
            msg = self._readObj()
            cmd = msg["command"]
            if cmd == 'tickPrices':
                self.event_handlers.on_price_update(msg['data'])
            elif msg["command"] == 'trade':
                self.event_handlers.on_trade_update(msg['data'])
            elif msg["command"] == "balance":
                self.event_handlers.on_balance_update(msg['data'])
            elif msg["command"] == "tradeStatus":
                self.event_handlers.on_trade_status_update(msg['data'])
            elif msg["command"] == "profit":
                self.event_handlers.on_profit_update(msg['data'])
            elif msg["command"] == "news":
                self.event_handlers.on_news_update(msg['data'])
            else:
                # Anything else
                self.event_handlers.on_unhandled_update(msg['data'])

    def set_handler(self, new_handler: IEventHandlers):
        self.event_handlers = new_handler

    # XTB subscription stuff
    def subscribePrice(self, symbol):
        self.execute(dict(command='getTickPrices', symbol=symbol, streamSessionId=self._ssId))

    def subscribePrices(self, symbols):
        for symbolX in symbols:
            self.subscribePrice(symbolX)

    def subscribeTrades(self):
        self.execute(dict(command='getTrades', streamSessionId=self._ssId))

    def subscribeBalance(self):
        self.execute(dict(command='getBalance', streamSessionId=self._ssId))

    def subscribeTradeStatus(self):
        self.execute(dict(command='getTradeStatus', streamSessionId=self._ssId))

    def subscribeProfits(self):
        self.execute(dict(command='getProfits', streamSessionId=self._ssId))

    def subscribeNews(self):
        self.execute(dict(command='getNews', streamSessionId=self._ssId))

    def unsubscribePrice(self, symbol):
        self.execute(dict(command='stopTickPrices', symbol=symbol, streamSessionId=self._ssId))

    def unsubscribePrices(self, symbols):
        for symbolX in symbols:
            self.unsubscribePrice(symbolX)

    def unsubscribeTrades(self):
        self.execute(dict(command='stopTrades', streamSessionId=self._ssId))

    def unsubscribeBalance(self):
        self.execute(dict(command='stopBalance', streamSessionId=self._ssId))

    def unsubscribeTradeStatus(self):
        self.execute(dict(command='stopTradeStatus', streamSessionId=self._ssId))

    def unsubscribeProfits(self):
        self.execute(dict(command='stopProfits', streamSessionId=self._ssId))

    def unsubscribeNews(self):
        self.execute(dict(command='stopNews', streamSessionId=self._ssId))


class XTBClient(IBroker):
    def __init__(self, address: str = 'xapi.xtb.com', port: int = 5124, encrypt=True):
        # Socket parameters
        self._maxConnectionRetries = 3
        self._apiTimeout = 100

        self._ssl = encrypt
        if not self._ssl:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket = ssl.wrap_socket(sock)
        self.conn = self.socket
        self._timeout = None
        self._address = address
        self._port = port
        self._decoder = json.JSONDecoder()
        self._receivedData = ''

        # XTB Streaming client injection
        self.streamSessionId = None
        self.streaming = None

        if not self._connect():
            raise Exception("Cannot connect to API on " + address + ":" + str(port) + " after " + str(
                self._maxConnectionRetries) + " retries")

    # START Socket section
    def _connect(self):
        for i in range(self._maxConnectionRetries):
            try:
                self.socket.connect((self._address, self._port))
            except socket.error as msg:
                time.sleep(0.25)
                continue
            return True
        return False

    def _sendObj(self, obj: dict):
        msg = json.dumps(obj)
        self._waitingSend(msg)

    def _waitingSend(self, msg: str):
        if self.socket:
            sent = 0
            msg = msg.encode('utf-8')
            while sent < len(msg):
                sent += self.conn.send(msg[sent:])
                time.sleep(self._apiTimeout / 1000)

    def _read(self, bytes_size: int = 4096):
        if not self.socket:
            raise RuntimeError("socket connection broken")
        resp = None
        while True:
            char = self.conn.recv(bytes_size).decode()
            self._receivedData += char
            try:
                (resp, size) = self._decoder.raw_decode(self._receivedData)
                if size == len(self._receivedData):
                    self._receivedData = ''
                    break
                elif size < len(self._receivedData):
                    self._receivedData = self._receivedData[size:].strip()
                    break
            except ValueError as e:
                continue
        return resp

    def _readObj(self):
        msg = self._read()
        return msg

    def close(self):
        self._closeSocket()
        if self.socket is not self.conn:
            self._closeConnection()

    def _closeSocket(self):
        self.socket.close()

    def _closeConnection(self):
        self.conn.close()

    # END Socket Section
    # START API Section

    def execute(self, dictionary):
        """Sends a JSON formatted request to the API

        Args:
            dictionary: A serializable python dict object.

        Returns:
            A raw JSON-encoded string response as received from the API.
        """
        self._sendObj(dictionary)
        return self._readObj()

    def _disconnect(self):
        """
        Closes the socket connection to the API.

        Returns:
            None
        """
        self.close()

    def commandExecute(self, commandName: str, arguments: Union[dict, None] = None):
        """Formats and executes a command into the XTB API.
        This is the preferred way of executing commands against the API as it ensures that the format is correct.

        Args:
            commandName: The command to be executed
            arguments: A dictionary with the command arguments.

        Returns:
            A raw JSON-encoded string response as received from the API.

        """
        if arguments is None:
            arguments = dict()
        cmd = dict([('command', commandName), ('arguments', arguments)])
        return self.execute(cmd)

    # END API Section
    # START Custom Section
    def verify_response(self, response: dict) -> dict:
        """Verifies that the response received from XTB is successful, else raises error.

        Validates the response received from the XTB API Connector and extracts the data portion from it.

        Args:
            response: A XTB client response object.

        Returns:
            A dict mapping containing the extracted response data from the passed response object. For example:
            {
                "balance": 995800269.43,
                "credit": 1000.00,
                "currency": "PLN",
                "equity": 995985397.56,
                "margin": 572634.43,
                "margin_free": 995227635.00,
                "margin_level": 173930.41
            }

        Raises:
            AssertionError: The response code received indicated that the operation was not successful.
        """
        if not response.get("status", False):
            raise AssertionError("Operation was not successful.")

        return response['returnData']

    def connect(self, user: Union[int, str] = None, password: str = None) -> bool:
        login_response = self.commandExecute('login', dict(userId=user, password=password))
        if login_response['status'] is False:
            print(
                f"Authentication error. Error code: {login_response['errorCode']}\nError message: {login_response['errorDescr']}")
            return self.authenticated

        self.streamSessionId = login_response['streamSessionId']
        self.streaming = XTBStreamingClient(self.streamSessionId)
        self.authenticated = login_response['status']
        return self.authenticated

    def connect_with_credentials(self, credentials: Credentials) -> bool:
        if credentials.is_token:
            raise TypeError("XTB cannot accept a token credentials.")
        return self.connect(credentials.username, credentials.password)

    def disconnect(self) -> None:
        """
        Cleanly shuts down the API connection, first logging out,
        then disconnecting the streaming client, and finally the socket.

        Returns:
            None
        """
        self.commandExecute('logout')
        self.streaming.disconnect()
        self._disconnect()

    def get_symbol(self, symbol: Union[str, Symbol]) -> Symbol:
        if type(symbol) == str:
            symbol_command = self.commandExecute("getSymbol", dict(symbol=symbol))
        elif type(symbol) == Symbol:
            symbol_command = self.commandExecute("getSymbol", dict(symbol=symbol.ticker))
        else:
            raise TypeError("Passed parameter is not of type Symbol or str.")

        # Return result
        symbol = self.verify_response(symbol_command)
        return Symbol(ticker=symbol['symbol'],
                      ask=symbol['ask'],
                      bid=symbol['bid'],
                      category=symbol['categoryName'],
                      contract_size=symbol['contractSize'],
                      currency=symbol['currency'],
                      currency_pair=symbol['currencyPair'],
                      currency_profit=symbol['currencyProfit'],
                      description=symbol['description'],
                      expiration=symbol['expiration'],
                      high=symbol['high'],
                      initial_margin=symbol['initialMargin'],
                      leverage=symbol['leverage'],
                      long_only=symbol['longOnly'],
                      min_lot=symbol['lotMin'],
                      max_lot=symbol['lotMax'],
                      lot_step=symbol['lotStep'],
                      low=symbol['low'],
                      pip_precision=symbol['pipsPrecision'],
                      price_precision=symbol['precision'],
                      shortable=symbol['shortSelling'],
                      time=TimeStamp(symbol['time'], unix=True, milliseconds=True)
                      )

    def get_available_symbols(self) -> List[Symbol]:
        response = self.commandExecute('getAllSymbols')
        symbols = self.verify_response(response)
        available_symbols = []
        for symbol in symbols:
            s = Symbol(ticker=symbol['symbol'],
                       ask=symbol['ask'],
                       bid=symbol['bid'],
                       category=symbol['categoryName'],
                       contract_size=symbol['contractSize'],
                       currency=symbol['currency'],
                       currency_pair=symbol['currencyPair'],
                       currency_profit=symbol['currencyProfit'],
                       description=symbol['description'],
                       expiration=symbol['expiration'],
                       high=symbol['high'],
                       initial_margin=symbol['initialMargin'],
                       leverage=symbol['leverage'],
                       long_only=symbol['longOnly'],
                       min_lot=symbol['lotMin'],
                       max_lot=symbol['lotMax'],
                       lot_step=symbol['lotStep'],
                       low=symbol['low'],
                       pip_precision=symbol['pipsPrecision'],
                       price_precision=symbol['precision'],
                       shortable=symbol['shortSelling'],
                       time=TimeStamp(symbol['time'], unix=True, milliseconds=True)
                       )
            available_symbols.append(s)

        return available_symbols

    def get_commission(self, volume: float, symbol: Union[str, Symbol]) -> Commission:
        if type(symbol) == str:
            res = self.commandExecute("getCommissionDef", dict(symbol=symbol, volume=volume))
        elif type(symbol) == Symbol:
            res = self.commandExecute("getCommissionDef", dict(symbol=symbol.ticker, volume=volume))
        else:
            raise TypeError("Passed parameter is not of type Symbol or str.")

        commission = self.verify_response(res)

        return Commission(commission=commission['commission'],
                          exchange_rate=commission['rateOfExchange'])

    def get_current_user_data(self) -> User:
        raise NotImplementedError("This feature is still under development.")

    def get_account_balance(self) -> AccountBalance:
        res = self.commandExecute("getMarginLevel")
        data = self.verify_response(res)
        return AccountBalance(
            balance=data["balance"],
            credit=data['credit'],
            currency=data['currency'],
            equity=data['equity'],
            margin=data['margin'],
            free_margin=data['margin_free']
        )

    def get_server_time(self) -> TimeStamp:
        res = self.commandExecute("getServerTime")

        data = self.verify_response(res)
        return TimeStamp(time_value=data['time'], unix=True, milliseconds=True)

    def get_version(self) -> str:
        res = self.commandExecute("getVersion")

        return self.verify_response(res)['version']

    def connection_status(self) -> bool:
        res = self.commandExecute("ping")
        return res.get("status", False)

    def check_transaction_status(self, transaction: TradeTransaction) -> bool:
        res = self.commandExecute("tradeTransactionStatus", dict(order=transaction.order_number))
        return self.verify_response(res)['requestStatus']

    def open_position(self, transaction: TradeTransaction) -> TradeTransaction:
        tt_info = {
            'cmd': transaction.operation,
            'customComment': transaction.comment,
            'expiration': transaction.expiration,
            'offset': transaction.trailing_offset,
            'order': transaction.order_number,
            'price': transaction.price,
            'sl': transaction.stop_loss_price,
            'symbol': transaction.symbol.ticker,
            'tp': transaction.take_profit_price,
            'type': transaction.transaction_type,
            'volume': transaction.volume
        }

        res = self.commandExecute("tradeTransaction", dict(tradeTransInfo=tt_info))
        transaction.order_number = self.verify_response(res)['order']
        return transaction

    # END Custom Section

