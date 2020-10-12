#   hokohoko/entities/_Account.py
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
#   Contains the definition of Hokohoko's Account object.
#

from typing import Dict, List, Union

import numpy as np

from hokohoko.entities._Order import Order
from hokohoko.entities._Position import Position


class Account:
    """
    Holds real-time information about the account during benchmarking.

    """

    #: The amount of account currency used per position.
    POSITION_OPEN_VALUE = 1000.0

    def __init__(self):
        """
        Provides access to the following data structures:

        **balance**

            A ``list[numpy.float64]`` of per-minute balances for the
            testing period. Starts with an initial balance of ``0.0``.
            Current balance can be retrieved via
            ``self.account.balance[-1]``.

        **equity**

            A ``list[numpy.float64]`` of per-minute equity for the
            testing period. Starts with an initial value of ``0.0``.
            Current equity can be retrieved via
            ``self.account.equity[-1]``.

        **orders**

            The ``list[hokohoko.entities.Order]`` temporarily containing
            the Orders placed by ``predictor.place_order[s]``. These get
            actioned at the end of the minute/bar in which they were
            placed, after closing requests have been actioned.

        **positions**

            The ``dict[numpy.int64, hokohoko.entities.Position]`` of
            Positions that are considered 'open'. These are made
            available to the Predictor (so can be manually closed), but
            their primary purpose is to keep a running record of balance
            and equity.

        **history**

            The ``list[hokohoko.entities.Positions]`` that will be passed
            into the Assessors.

        **symbol_ids**

            The ``list[str]`` of symbols available to this account.
            Order should match that of returned Bars.

        """
        self.balance: List[Union[float, np.float64]] = [0.0]
        self.equity: List[Union[float, np.float64]] = [0.0]
        self.orders: Dict[int, Order] = {}
        self.positions: Dict[int, Position] = {}
        self.history: Dict[int, Position] = {}
        self.symbol_ids: List[str] = []
