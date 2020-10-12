#   hokohoko/standard/__init__.py
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
#   Contains a standard Data source, Predictor and Assessor. These do
#   nothing except load the data and cycle through it.
#

__all__ = [
    "DoNothing",
    "Logger",
    "Npz"
]

from hokohoko.standard._DoNothing import DoNothing
from hokohoko.standard._Logger import Logger
from hokohoko.standard._Npz import Npz
