#   hokohoko/standard/_DoNothing.py
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
#   This is a dummy predictor, which makes no predictions.
#

from typing import Iterable

from hokohoko.entities import Bar, Predictor


class DoNothing(Predictor):
    """
    This Predictor does nothing at all, which causes Hokohoko to
    generate a lot of DONT_BUY, DONT_SELL Orders.
    """

    def __enter__(self) -> Predictor:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def on_start(self, bars: Iterable[Bar]) -> None:
        pass

    def on_bar(self, bars: Iterable[Bar]) -> None:
        pass

    def on_stop(self) -> None:
        pass
