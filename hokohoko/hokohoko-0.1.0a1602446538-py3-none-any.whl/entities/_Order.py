#   hokohoko/entities/_Order.py
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
#   Contains the definition of Hokohoko's Order object.
#
from typing import NamedTuple, Optional, Union

import numpy as np

from hokohoko import utils
from hokohoko.entities._Direction import Direction


class Order(NamedTuple):
    """
    An order is a request for a trade within the FOREX environment.

    .. note ::

        If setting both ``take_profit`` and ``stop_loss`` to ``None``,
        the resultant Order and/or Position will automatically be closed
        at the end of the Bar.

    """

    #: [numpy.int64] The ID of the symbol trade is requested for.
    symbol_id: Union[int, np.int64]

    #: [hokohoko.entities.Direction] What direction the trade is.
    direction: Direction

    #: [numpy.float32] At what rate the Order will open a Position.
    #: Can be set to ``None`` to specify open immediately at the current
    #: price.
    open_bid: Optional[Union[float, np.float32]] = None

    #: [numpy.float32] At what rate the resultant Position should close
    #: to realise profits. Can be set to ``None``.
    take_profit: Optional[Union[float, np.float32]] = None

    #: [numpy.float32] At what rate the resultant Position should close
    #: to restrict losses. Can be set to ``None``.
    stop_loss: Optional[Union[float, np.float32]] = None

    def __str__(self):
        return "Order:({}, {}, {}, {}, {})".format(
            utils.convert_id_to_symbol(self.symbol_id),
            self.direction.name,
            f"{self.open_bid:.5f}" if self.open_bid is not None else "None",
            f"{self.take_profit:.5f}" if self.take_profit is not None else "None",
            f"{self.stop_loss:.5f}" if self.stop_loss is not None else "None"
        )

    def __repr__(self):
        return self.__str__()
