#   hokohoko/data/_Npz.py
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
#   Contains an implementation of Hokohoko's Data interface, which uses
#   numpy's .npz format.
#

import multiprocessing as mp
from typing import Iterable, Optional

import numpy as np

from hokohoko import utils
from hokohoko.entities import Data


class Npz(Data):

    def __init__(
            self,
            parameters: str,
            symbol_subset: Optional[Iterable[str]] = None,
            origin: int = 0,
            end: Optional[int] = None,
            lock: Optional[mp.Lock] = None,
            load: bool = True
    ) -> None:
        """
        :param parameters:      A string of arguments, from
                                ``HokohokoConfig.data_parameters``.
                                See Parameter Arguments below for
                                details.
        :type parameters:       str

        :param symbol_subset:   A comma-separated string of specific
                                symbols to load. If the requested symbol
                                doesn't exist in the data set it is
                                ignored. This list may be augmented by
                                other currency pairs required to convert
                                Orders to the Account base currency.
        :type symbol_subset:    str

        Other arguments are internal to Hokohoko.

        **Parameters Arguments:**

            .. code-block:: Text

                filename [start_override=TIMESTAMP] [end_override=TIMESTAMP]

                    filename        The name of the data file to load.

                    start_override  Specify the timestamp within the
                                    data to load from.
                                    [Not implemented yet]

                    end_override    Specify the timestamp within the
                                    data to stop at.
                                    [Not implemented yet]

        **The Data File:**

            The Hokohoko data.npz file contains 3 records:

            1. Symbols available. This is a comma-separated list of
               currency pairs available in the data.
            2. Timestamps. This is an array of numpy.float64s
               representing the UTC timestamp for each data period.
            3. Exchange rate data. This is a 2D array of data, ordered
               by symbol then timestamp. The lines are in the same order
               as the Symbols available, likewise the data for
               timestamps. Each packet of data contains five data
               points: ``OPEN``, ``HIGH``, ``LOW``, ``CLOSE`` and
               ``VOLUME``.

            .. include:: downloads.rst

        **Performance Issues:**

            Due to Windows caching issues, Hokohoko uses a shared
            ``multiprocessing.lock`` to synchronise access to the data
            file. Also due to Windows, the RAM requirements [currently,
            version |version|] are significant - approximately 1GB per
            current process.

        """
        super().__init__(parameters, symbol_subset, origin, end, lock, load)

    @utils.generate_tests("""
        raises an error if parameters has no filename
        raises an error if file doesn't exist
        raises an error if start_override is negative
        raises an error if end_override is less than start_override
        raises an error if symbol_subset is not a string
        raises an error if origin is negative
        raises an error if end is less than origin
        raises an error if lock is not a lock
        loads all the symbols correctly
        loads only the specified symbols
        loads the requested timestamps only
        loads the requested data only
        doesnt load data if load is false
    """)
    def __enter__(self) -> 'Npz':
        """
        Opens the numpy.npz file configured via the initialization
        parameters provided in Data.__init__. This uses a shared lock if
        available, because in Windows, the full file is loaded every
        time, causing excessive RAM usage.
        """

        if self.origin < 0:
            raise ValueError("origin < 0")
        if self.end is not None and self.end <= self.origin:
            raise ValueError("end <= origin")

        if self.lock is not None:
            self.lock.acquire()

        with np.load(self.parameters, mmap_mode='r') as source:
            # 1. Build list of symbols and their indexes.
            _symbol_ids = source['symbol_ids']
            if self.symbol_subset is not None:
                self.symbol_ids = np.array([
                    s for s in _symbol_ids if utils.convert_id_to_symbol(s) in self.symbol_subset
                ])
            else:
                self.symbol_ids = _symbol_ids
            _symbol_indexes = np.array(
                [i for i, s in np.ndenumerate(_symbol_ids) if s in self.symbol_ids]
            )

            # 2. Load the data.
            if self.end is not None:
                self.timestamps = source['timestamps'][self.origin:self.end]
                if self.load:
                    self.data = (
                        source['data'][_symbol_indexes, self.origin * 5:self.end * 5]
                    )[:, 0, :]
            else:
                self.timestamps = source['timestamps'][self.origin:]
                if self.load:
                    self.data = (source['data'][_symbol_indexes, self.origin * 5:])[:, 0, :]

        if self.lock is not None:
            self.lock.release()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Nothing to clean up.

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:

        """
        pass

    @utils.generate_tests("returns the correct symbol ids")
    def get_symbol_ids(self) -> np.ndarray:
        """
        Returns the list of symbols currently available in the data
        source. If a subset was selected, this will be the intersection
        of symbols available and the requested subset. Additional
        symbols may be loaded for internal use if required.

        :return:    The list of available symbols (as ids).
        :rtype:     numpy.ndarray[numpy.int64]

        """
        return self.symbol_ids

    @utils.generate_tests("returns the correct count of minutes")
    def get_minutes(self) -> int:
        """
        Get how many minutes are available in this data source. This may
        vary depending on loading conditions.

        :returns:   Number of minutes.
        :rtype:     int

        """
        return self.timestamps.shape[0]

    @utils.generate_tests("""
        raises an error if origin is negative
        raises an error if end is less than origin
        returns two arrays
        first array returned is timestamps
        second array returned is exchange rate data
        returns expected data for all symbols
        returns expected data for specified symbols
    """)
    def get_partial_data(
            self,
            origin: int,
            end: int
    ) -> (np.ndarray, np.ndarray):
        """
        Retrieve a block of data [origin, end) from the source.

        :param origin:  The first minute to get. Note this is an index
                        value, with 0 being the start of the available
                        data.
        :type origin:   int

        :param end:     Get up to this minute.
        :type end:      int

        :returns:       | Two arrays:
                        | 1. Per-minute timestamps.
                        | 2. Per-symbol, per-minute exchange rate data.
        :rtype:         tuple(numpy.ndarray, numpy.ndarray)

        """
        if origin < 0:
            raise ValueError("origin < 0")
        if end <= origin:
            raise ValueError("end <= origin")

        origin, end = origin - self.origin, end - self.origin
        return self.timestamps[origin:end], self.data[:, origin * 5: end * 5]
