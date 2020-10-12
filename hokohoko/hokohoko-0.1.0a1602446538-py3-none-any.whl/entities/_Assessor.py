#   hokohoko/entities/_Assessor.py
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
#   Contains the definition of Hokohoko's Assessor object.
#
from typing import Iterable, Optional

from hokohoko import utils


class Assessor:
    """
    This is the base class for an assessor. It provides the following
    base attributes:

    .. code-block:: Text

        parameters      The parameter string given for this Assessor.

    """

    @utils.generate_tests("should set internal parameters")
    def __init__(self, parameters: Optional[str] = None) -> None:
        """
        Initialises the Assessor, saving the given parameters.

        :param parameters:  The parameters passed on configuration.
        :type parameters:   str

        """
        self.parameters = parameters

    def analyse(self, data: Iterable) -> None:
        """
        Analyse Hokohoko's benchmarking results.

        :param data:        The data to analyse. This is provided as an
                            Account per Period.
        :type data:         list[multiprocessing.pool.AsyncResult[tuple[int, hokohoko.entities.Account]]]

        .. include:: must_override.rst

        """
        raise NotImplementedError
