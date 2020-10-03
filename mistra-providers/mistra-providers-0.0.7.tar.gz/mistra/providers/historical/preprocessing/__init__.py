import csv, os
from datetime import timedelta
from numpy import array
import pandas as pd
from mistra.core.intervals import Interval
from mistra.core.pricing import Candle
from mistra.core.sources import Source


def dump(source, file_pattern, interval=Interval.DAY):
    """
    Takes a source of candles and stores its contents in several chunks. The chunk size will
      be the ratio of the given interval by the source's interval. For this to work, some things
      are required to happen:

      - The given source must be of candle type.
      - The given interval must be exactly divisible by the source's interval.
      - Each chunk will be stored according to the given file pattern, which must have a format
          according to strftime/strptime datetime functions.

    Please note: THE FILES'S CONTENTS DO NOT KEEP ANY KIND OF TRACK OF TIMESTAMPS -neither base
      or per-candle timestamps- OR INTERVAL SIZES. Please make sure you state somewhere what
      interval size and base date are you dealing with when loading one of those dumps (e.g. use
      an appropriate file pattern reflecting the interval size, and use all the markers you'd need
      for the date/time). You can have for sure that the used timing is regular (i.e. all the
      candles have the same time width).

    :param source: The source to chunk.
    :param file_pattern: The destination of the files.
    :param interval: The interval the source will be chunked by. By default, one day. It could be less.
      This means: chunks will span a period of 1 day, or the given interval.
    """

    if source.dtype != Candle:
        raise ValueError("Given source must use underlying Candle types to work")
    interval_size = int(interval)
    ratio, remainder = divmod(interval_size, int(source.interval))
    if remainder:
        raise ValueError("Given interval must be exactly divisible by source's interval")
    length = len(source)
    current_chunk_date = source.timestamp
    for idx in range(0, length, ratio):
        chunk = source[idx:min(idx + ratio, length)]
        concrete_file_pattern = current_chunk_date.strftime(file_pattern)
        os.makedirs(os.path.dirname(concrete_file_pattern), 0o755, True)
        with open(current_chunk_date.strftime(file_pattern), 'w') as output:
            writer = csv.writer(output)
            for chunk_idx in range(0, chunk.shape[0]):
                bid_candle = chunk[chunk_idx, 0]
                ask_candle = chunk[chunk_idx, 1]
                writer.writerow((bid_candle.start, ask_candle.start,
                                 bid_candle.min, ask_candle.min,
                                 bid_candle.max, ask_candle.max,
                                 bid_candle.end, ask_candle.end))
        current_chunk_date += timedelta(seconds=interval_size)


def load(fileobj, interval, base_timestamp, initial_bid=None, initial_ask=None):
    """
    Given a file name or file object, an interval, and a base timestamp (and other optional arguments)
      it loads candle data from a 4-column CSV file and makes a source frame with that.

    :param fileobj: The source file object (or name).
    :param interval: The interval to consider (beforehand known that interval is the appropriate).
    :param base_timestamp: The base timestamp to use (beforehand known the source corresponds to it).
    :param initial_bid: The initial buy value (beforehand known that value was the end buy price in the
      previous market data).
    :param initial_ask: The initial buy value (beforehand known that value was the end buy price in the
      previous market data).
    :return:
    """

    if not isinstance(initial_bid, Candle) and initial_bid is not None:
        initial_bid = Candle.constant(initial_bid)
    if not isinstance(initial_ask, Candle) and initial_ask is not None:
        initial_ask = Candle.constant(initial_ask)
    pd_csv = pd.read_csv(fileobj, chunksize=3600, header=None)
    source = Source(Candle, base_timestamp, interval, initial_bid, initial_ask)
    rows = []
    for chunk in pd_csv:
        for idx, row in chunk.iterrows():
            rows.append((Candle(start=row[0], min=row[2], max=row[4], end=row[6]),
                         Candle(start=row[1], min=row[3], max=row[5], end=row[7])))
    source.push(array(rows, dtype=Candle))
    return source
