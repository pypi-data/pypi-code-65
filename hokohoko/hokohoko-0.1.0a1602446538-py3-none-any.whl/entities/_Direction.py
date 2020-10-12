#   hokohoko/entities/_Direction.py
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
#   Contains the definition of Hokohoko's Direction object.
#

from enum import Enum


class Direction(Enum):
    """
    Specifies the requested trade direction when placing an Order.

    """

    #: Specifies a buy trade (exchange rate expected to increase).
    BUY = 0

    #: Specified a sell trade (exchange rate expected to decrease).
    SELL = 1

    #: Lets the benchmark know not buying this symbol is deliberate.
    #: Auto-generated in the absence of an appropriate ``BUY``.
    DONT_BUY = 2

    #: Lets the benchmark know not selling this symbol is deliberate.
    #: Auto-generated in the absence of an appropriate ``SELL``.
    DONT_SELL = 3
