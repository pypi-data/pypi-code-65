#   hokohoko/_period.py
#
#   Copyright 2020 Neil Bradley
#
#   This file is part of Hokohoko.
#
#   Hokohoko is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Hokohoko is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY# without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Hokohoko.  If not, see <https://www.gnu.org/licenses/>.
#
#   ====================================================================
#
#   This file contains the definition of a Period object.  In Hokohoko,
#   a Period refers to a single contiguous era of testing.
#

"""
======
Period
======

A Period is a single time slice which Hokohoko benchmarks across.
"""
from typing import List, NamedTuple

import numpy as np

from hokohoko import utils
from hokohoko.entities import Bar, Data


class PeriodConfig(NamedTuple):
    """
    Create a config containing individual period settings. All points
    are in minutes offset from start of data.
    """
    period_id: int
    origin: int
    test_point: int
    end: int
    available_symbols: np.ndarray


class Period:
    """
    Runs each individual training/testing period. Provides a shared lock
    to the Data and Predictor.
    """
    data_lock = None
    predictor_lock = None

    @staticmethod
    @utils.generate_tests("""sets internal locks correctly.""")
    def init(data_lock, predictor_lock):
        """
        Initializes the shared locks.

        :param data_lock:       Lock for data items.
        :param predictor_lock:  Lock for predictors to share.
        """
        Period.data_lock = data_lock
        Period.predictor_lock = predictor_lock


@utils.generate_tests("""
    raises an error if the data source does not inherit hokohoko.entities.Data
    raises an error if minute is negative
    raises an error if past_minutes is negative
    raises an error if minute is past end of source
    returns a List of Bars.
    the order of the Bars in the list don't change between calls.
    if minute is zero, all fields should be the data's open value.
""")
def get_last_close_at_minute(
        source: Data,
        minute: int,
        past_minutes: int
) -> List[Bar]:
    """
    Gets the first set of data for the predictor. This is made up of all
    the open values for the given minute. The last close minute is
    always flat - i.e. open == high == low == close, with a volume of 0.

    :param source:              The data source.
    :param minute:              The minute which will have the opening
                                values calculated at.
    :param past_minutes:        How many prior minutes to pretend there
                                were.

    :returns:                   The last close bars.
    """
    timestamps, data = source.get_partial_data(minute, minute + 1)
    return [Bar(
        source.symbol_ids[i],
        e[0],
        e[0],
        e[0],
        e[0],
        0.0,
        timestamps[0] - past_minutes * 60,
        timestamps[0]
    ) for i, e in enumerate(data)]


@utils.generate_tests("""
    raises an error if the data source does not inherit hokohoko.entities.Data
    raises an error if minute is not N
    raises an error if minute is past end of source
    returns a list of Bars.
    the order of the Bars in the list don't change between calls.
    if minute is 1, should match the data.
""")
def get_past_minute(
        source: Data,
        minute: int
) -> List[Bar]:
    """
    Retrieves the Bars for the specified minute.

    :param source:              The data source.
    :param minute:              The minute we are checking.

    :returns:                   The past Bars as specified.
    """
    timestamps, data = source.get_partial_data(minute - 1, minute)
    return [Bar(
        source.symbol_ids[i],
        *e[0:5],
        timestamps[0],
        timestamps[0] + 60
    ) for i, e in enumerate(data)]


@utils.generate_tests("""
    raises an error if the data source does not inherit hokohoko.entities.Data
    raises an error if start is negative
    raises an error if start is past end of source
    raises an error if end is less than start
    raises an error if end is past end of source
    returns a list of Bars
    the order of the Bars in the list don't change between calls.
    high values are highest from the data
    low values are lowest from the data
    volumes are sum of data volumes
    open matches first value open
    close matches last value close
    end timestamp is greater than start timestamp
""")
def get_past_minutes(
        source: Data,
        start: int,
        end: int
) -> List[Bar]:
    """
    Retrieves the Bars for the specified symbol subset and minutes.

    :param source:  The data source.
    :param start:   The start of the last Bar.
    :param end:     The end of the Bar we want.

    :returns:       A list of Bars covering the specified time period.
    """
    timestamps, data = source.get_partial_data(start, end)
    return [Bar(
        source.symbol_ids[i],
        e[0],
        np.max(e[1::5]),
        np.min(e[2::5]),
        e[-2],
        np.float32(np.sum(e[4::5])),
        timestamps[0],
        timestamps[-1] + 60
    ) for i, e in enumerate(data)]
