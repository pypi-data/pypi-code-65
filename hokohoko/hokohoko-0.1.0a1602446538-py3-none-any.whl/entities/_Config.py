#   hokohoko/entities/_Config.py
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
#   Contains the definition of Hokohoko's Config object.
#

from typing import NamedTuple, Optional

from hokohoko import defaults


class Config(NamedTuple):
    """
    Controls the behaviour of Hokohoko. Most of these values should not
    be changed.

    """

    #: The Predictor to use.
    predictor_class: str = defaults.DEFAULT_PREDICTOR_CLASS

    #: The Assessor to use.
    assessors: list = defaults.DEFAULT_ASSESSORS

    #: The type of data source to load.
    data_class: str = defaults.DEFAULT_DATA.split(maxsplit=1)[0]

    #: The data parameters.
    data_parameters: str = defaults.DEFAULT_DATA.split(maxsplit=1)[1]

    #: Comma-separated list of currency-pair names, or None for all.
    data_subset: Optional[str] = defaults.DEFAULT_DATA_SUBSET

    #: How many Periods to test.
    period_count: int = defaults.DEFAULT_PERIOD_COUNT

    #: The size of the process Pool (number of cores allocated).
    process_count: int = defaults.DEFAULT_PROCESS_COUNT

    #: How many minutes a bar in on_bar represents.
    past_minutes: int = defaults.DEFAULT_PAST_MINUTES

    #: How many minutes to 'Hold' an Order/Position till auto-close.
    hold_minutes: int = defaults.DEFAULT_HOLD_MINUTES

    #: How many minutes to make available for testing from. Should be
    #: greater than sum(training_minutes, test_minutes, hold_minutes),
    #: or None for unlimited.
    load_limit: Optional[int] = defaults.DEFAULT_LOAD_LIMIT

    #: How many minutes to train the Predictor on before
    #: assessing/accepting trades. Not necessarily contiguous.
    training_minutes: int = defaults.DEFAULT_TRAINING_MINUTES

    #: How many minutes to test for. Sequential, but not necessarily
    #: contiguous.
    test_minutes: int = defaults.DEFAULT_TEST_MINUTES

    #: Enable profiling output in the current directory.
    profiling: bool = defaults.DEFAULT_PROFILING
