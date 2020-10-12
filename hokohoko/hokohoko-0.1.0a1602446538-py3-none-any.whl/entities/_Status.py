#   hokohoko/entities/_Status.py
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
#   Contains the definition of Hokohoko's Status object.
#

from enum import Enum


class Status(Enum):
    """
    Indicates the outcome for the given Order/Position.

    """
    #: The Position is awaiting activation (still an Order).
    PENDING = 0

    #: The Position is open (active).
    OPEN = 1

    #: The Position was closed either manually or automatically.
    CLOSED = 2

    #: The Position closed when its ``take_profit`` condition was met.
    CLOSED_TAKE_PROFIT = 3

    #: The Position closed when its ``stop_loss`` condition was met.
    CLOSED_STOP_LOSS = 4

    #: The Order was deliberately not taken in Benchmark mode.
    NOT_TAKEN = 5

    def __repr__(self):
        return self.name
