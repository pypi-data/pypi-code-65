#   hokohoko/__init__.py
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
#   Logs the output of Positions in a readable format, along with
#   running balance and equity totals.
#

from typing import Iterable

import numpy as np

from hokohoko.entities import Assessor


class Logger(Assessor):

    def analyse(self, data: Iterable) -> None:
        # TODO: Make this output per-Order rather than total equity.
        results = np.array([a.get()[1].equity[-1] for a in data], dtype=np.float64)
        for i, r in enumerate(results):
            print(f"{i:03d}:{r:12.2f}")
