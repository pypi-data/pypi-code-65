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
        chunk.shape = chunk.shape[0:1]
        concrete_file_pattern = current_chunk_date.strftime(file_pattern)
        os.makedirs(os.path.dirname(concrete_file_pattern), 0o755, True)
        with open(current_chunk_date.strftime(file_pattern), 'w') as output:
            writer = csv.writer(output)
            for chunk_idx in range(0, chunk.shape[0]):
                candle = chunk[chunk_idx]
                writer.writerow((candle.start, candle.min, candle.max, candle.end))
        current_chunk_date += timedelta(seconds=interval_size)


def load(fileobj, interval, base_timestamp, initial=None):
    """
    Given a file name or file object, an interval, and a base timestamp (and other optional arguments)
      it loads candle data from a 4-column CSV file and makes a source frame with that.

    :param fileobj: The source file object (or name).
    :param interval: The interval to consider (beforehand known that interval is the appropriate).
    :param base_timestamp: The base timestamp to use (beforehand known the source corresponds to it).
    :param initial: The initial value (beforehand known that value was the end price in the previous market data).
    :return:
    """

    if not isinstance(initial, Candle) and initial is not None:
        initial = Candle.constant(initial)
    pd_csv = pd.read_csv(fileobj, chunksize=3600, header=None)
    source = Source(Candle, base_timestamp, interval, initial)
    rows = []
    for chunk in pd_csv:
        for idx, row in chunk.iterrows():
            rows.append(Candle(start=row[0], min=row[1], max=row[2], end=row[3]))
    data = array(rows, dtype=Candle)
    data.shape = (data.shape[0], 1)
    source.push(data)
    return source
