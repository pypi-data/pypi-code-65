"""
TrueFX datasets are a particular case of CSV datasets (in fact: the default arguments
  of the CSV datasets are suitable for the TrueFX datasets).
"""


from mistra.core.intervals import Interval
from ..filesystem import CSVBackTestingProvider


class TrueFXBackTestingProvider(CSVBackTestingProvider):
    """
    A sub-class of CSV back-testing provider, suited to the format of
      TrueFX data sources.
    """

    def __init__(self, fileobj, base_timestamp, initial_buy, initial_sale, chunk_size=3600, price_precision=4):
        """
        Creates a setting to load data from a file object.
        :param fileobj: The file (name or object) to read from.
        :param base_timestamp: The base date[time] to use for the generated sources. It will be truncated to
          its month, ignoring everything else.
        :param initial_buy: The initial buy non-standardized price (as string!).
        :param initial_sale: The initial sale non-standardized price (as string!).
        :param chunk_size: The chunk size for the sources, and the reads.
        :param price_precision: The precision -pip depth, say- to standardize prices.
        """

        base_timestamp = base_timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        super().__init__(fileobj, base_timestamp, initial_buy, initial_sale, Interval.SECOND, chunk_size,
                         '%Y%m%d %H:%M:%S.%f', 1, 2, 3, price_precision)
