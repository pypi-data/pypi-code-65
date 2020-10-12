#   hokohoko/entities/_Data.py
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
#   Contains the definition of Hokohoko's Data object.
#

import multiprocessing as mp
from typing import Iterable, Optional

import numpy as np

from hokohoko import utils


class Data:
    """
    Defines the interface for a data source. Hokohoko interacts with the
    Data through a ``with`` block, so ``__enter__`` and ``__exit__``
    should both be overridden. The provided interface assumes using a
    memory cache for speed, and thus it is expected that generally data
    acquisition will be done during ``__enter__`` with the internal
    parameters provided.

    """

    @utils.generate_tests("sets internal values correctly")
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
        :param parameters:      The parameters specific to this data
                                source, e.g. filename. Stored in
                                ``self.parameters``.
        :type parameters:       str

        :param symbol_subset:   (Optional) The requested symbol list.
                                Stored in ``self.symbol_subset``.
        :type symbol_subset:    List[str]

        :param origin:          (Optional) The minute to load from
                                (inclusive). This is an index value
                                (with ``0`` he first minute available in
                                the source. Stored in ``self.origin``.
        :type origin:           int

        :param end:             (Optional) The minute load up to. Stored
                                in ``self.end``.
        :type end:              int

        :param lock:            A single Lock shared by all instances of
                                this type.
        :type lock:             multiprocessing.Lock

        :param load:            Indicates if the data is being loaded or
                                not. For a significant speed boost,
                                Hokohoko first initialises the data
                                source once with this as ``False`` to
                                request the information required to
                                configure Periods. Each individual
                                period process then loads it, with the
                                value ``True``.

                                As Hokohoko asks for the available
                                symbols and minutes, this should only be
                                used to control lazy loading of
                                ``self.data``.
        :type load:             bool

        **Internal data items available:**

            These internal items are initially ``None``, and should be
            set (if used) during ``__enter__``.

            .. code-block:: Text

                symbol_ids:     The intersection of available and
                                requested symbols.

                timestamps:     The per-minute UTC timestamps for the
                                cached data.

                data:           The data cache
                                (len(symbols_ids), origin:end).

        """
        self.parameters = parameters
        self.symbol_subset = symbol_subset
        self.origin = origin
        self.end = end
        self.lock = lock
        self.load = load

        self.symbol_ids = None
        self.timestamps = None
        self.data = None

    def __enter__(self) -> 'Data':
        """
        Called upon entry into a with block. This should connect to the
        data source using the already supplied parameters.

        :returns:   This should return ``self``.
        :rtype:     hokohoko.entities.Data

        .. include:: must_override.rst

        """
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when a with block is exited, either normally or through
        an exception. This should disconnect, close and release the data
        source.

        .. include:: must_override.rst

        """
        raise NotImplementedError

    def get_symbol_ids(self) -> np.ndarray:
        """
        Returns the list of symbols currently available in the data
        source. If a subset was selected, this will be the intersection
        of symbols available and the requested subset. Note that
        Hokohoko requests additional symbols for internal use if
        required.

        :return:    The list of available symbols (as ids).
        :rtype:     numpy.ndarray[numpy.int64]

        .. include:: must_override.rst

        """
        raise NotImplementedError

    def get_minutes(self) -> int:
        """
        Get how many minutes are available in this data source. This
        should be the total amount of minutes in the data source if
        ``load == False``, otherwise how many have been cached
        (hopefully ``end - origin``).

        :returns:   Number of minutes.
        :rtype:     int

        .. include:: must_override.rst

        """
        raise NotImplementedError

    def get_partial_data(
            self,
            origin: int,
            end: int
    ) -> (np.ndarray, np.ndarray):
        """
        Retrieve a block of data [origin, end) from the source.

        :param origin:  The first minute to load from. Note this is an
                        index value, with 0 being the start of the
                        available data.
        :type origin:   int

        :param end:     The last minute to load.
        :type end:      int

        :returns:       | Two arrays:
                        | 1. Per-minute timestamps.
                        | 2. Per-symbol, per-minute exchange rate data.
        :rtype:         tuple(numpy.ndarray, numpy.ndarray)

        .. include:: must_override.rst

        """
        raise NotImplementedError
