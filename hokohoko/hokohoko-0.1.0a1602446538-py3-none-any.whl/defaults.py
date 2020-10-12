#   hokohoko/defaults.py
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
#   This file contains the default values for Hokohoko.
#

# Default options
DEFAULT_PREDICTOR_CLASS = 'hokohoko.standard.DoNothing'  #:
DEFAULT_ASSESSORS = ['hokohoko.standard.Logger']  #:
DEFAULT_DATA = 'hokohoko.standard.Npz data.npz'  #:
DEFAULT_DATA_SUBSET = None  #: Use all available Symbols.
DEFAULT_PERIOD_COUNT = 256  #: Number of separate Periods to run.
DEFAULT_PROCESS_COUNT = 8  #: Number of cores to use.
DEFAULT_PAST_MINUTES = 1440  #: Sets epochs to 1-day.
DEFAULT_HOLD_MINUTES = 1440  #: Assess for a 1-day epoch.
DEFAULT_LOAD_LIMIT = None  #: Load the full data set (no restriction).
DEFAULT_TRAINING_MINUTES = 10080 * 26 * 3  #: 18 months of weeks.
DEFAULT_TEST_MINUTES = 10080 * 26  #: 6 months of weeks.
DEFAULT_PROFILING = False  #: Don't enable Python's profiler.
