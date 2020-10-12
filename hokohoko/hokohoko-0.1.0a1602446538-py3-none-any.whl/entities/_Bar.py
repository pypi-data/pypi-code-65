#   hokohoko/entities/_Bar.py
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
#   Contains the definition of Hokohoko's Bar object.
#

from typing import NamedTuple, Union

import numpy as np

from hokohoko import utils


class Bar(NamedTuple):
    """
    Contains foreign exchange data for a single Symbol over a period of
    time.

    """

    #: An integer representation of the symbol. [``numpy.int64``]
    symbol_id: Union[int, np.int64]

    #: The exchange rate for this symbol at the open of this Bar. [``numpy.float32``]
    open: Union[float, np.float32]

    #: The highest exchange rate seen for this symbol during this Bar. [``numpy.float32``]
    high: Union[float, np.float32]

    #: The lowest exchange rate seen for this symbol during this Bar. [``numpy.float32``]
    low: Union[float, np.float32]

    #: The exchange rate for this symbol at the close of this Bar. [``numpy.float32``]
    close: Union[float, np.float32]

    #: The relative trade volume during this Bar. [``numpy.float32``]
    volume: Union[float, np.float32]

    #: The UTC timestamp at the start of this Bar. [``numpy.int64``]
    start: Union[int, np.int64]

    #: The UTC timestamp at the end of this Bar. [``numpy.int64``]
    end: Union[int, np.int64]

    def __str__(self):
        return "Bar:({}, {:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.0f}, {:.0f}, {:.0f})".format(
            utils.convert_id_to_symbol(self.symbol_id),
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
            self.start,
            self.end
        )

    def __repr__(self):
        return self.__str__()
