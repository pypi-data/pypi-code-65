"""
File-system based historical data (back-testing) providers exist here.

Since this is old data, file-system can safely use it.

One example: CSV data.
"""
from datetime import datetime
import pandas as pd
from mistra.core.intervals import Interval
from mistra.core.pricing import Candle
from mistra.core.providers import BackTestingProvider
from mistra.core.sources import Source


class CSVBackTestingProvider(BackTestingProvider):
    """
    Parses a CSV file and creates the two sources from it.
    """

    def __init__(self, fileobj, base_timestamp, initial_buy, initial_sale,
                 interval=Interval.SECOND, chunk_size=3600, timestamp_format='%Y%m%d %H:%M:%S.%f',
                 timestamp_column=1, buy_price_column=2, sale_price_column=3, price_precision=4):
        """
        Reads data from a CSV file.
        :param fileobj: The file (name or object) to read from.
        :param base_timestamp: The base date[time] to use for the generated sources. E.g. for truefx, it will be
          <year>-<month>-01 00:00:00.
        :param interval: The interval to srink the data into.
        :param chunk_size: The chunk size to use for the internal growing arrays.
        :param timestamp_format: The timestamp format to use when reading the timestamp column.
        :param initial_buy: Initial buy non-standardized price to use (e.g. the end price from previous work month).
        :param initial_sale: Initial sale non-standardized price to use (e.g. the end price from previous work month).
        :param timestamp_column: The column holding the timestamp.
        :param buy_price_column: The column with the buy price.
        :param sale_price_column: The column with the sale price (which will be bigger than buy price).
        :param price_precision: The precision to parse the decimals. /USD pairs must have 4 (which will
          turn into 5) while /JPY pairs must use 2 (which will turn into 3).
        """

        self._fileobj = fileobj
        self._base_timestamp = base_timestamp
        self._interval = interval
        self._chunk_size = chunk_size
        self._timestamp_format = timestamp_format
        self._timestamp_column = timestamp_column
        self._buy_price_column = buy_price_column
        self._sale_price_column = sale_price_column
        self._price_precision = price_precision
        self._initial_buy = Candle.constant(self._standardize(initial_buy))
        self._initial_sale = Candle.constant(self._standardize(initial_sale))

    def _standardize(self, price_string):
        """
        Standardizes a price, according to the current price precision.
        :return: The standardized price.
        """

        parts = price_string.split('.')
        frac_amount = int(parts[1].ljust(self._price_precision + 1, '0'))
        int_amount = int(parts[0]) * 10 ** (self._price_precision + 1)
        return int_amount + frac_amount

    def _execute(self):
        """
        Reads the CSV from a data frame.
        :return: A tuple with the (buy price, sale price).
        """

        csv = pd.read_csv(self._fileobj, chunksize=self._chunk_size, header=None,
                          dtype={self._buy_price_column: str, self._sale_price_column: str})
        source = Source(Candle, self._base_timestamp, self._interval, self._initial_buy, self._initial_sale)
        for chunk in csv:
            for idx, row in chunk.iterrows():
                stamp = datetime.strptime(row[self._timestamp_column], self._timestamp_format)
                buy_price = self._standardize(row[self._buy_price_column])
                sale_price = self._standardize(row[self._sale_price_column])
                self._merge(stamp, buy_price, sale_price, source)
        return source
