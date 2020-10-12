#   hokohoko/entities/_Predictor.py
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
#   Contains the definition of Hokohoko's Predictor object.
#
import multiprocessing as mp
from random import Random
from typing import Iterable, Optional

from hokohoko import utils
from hokohoko.entities._Account import Account
from hokohoko.entities._Bar import Bar
from hokohoko.entities._Order import Order


class Predictor(Random):
    """
    Defines the interface for a Predictor, and provides routines for
    order management.

    """

    _MAGIC_SEED = 0x484F4B4F

    @utils.generate_tests("""
        initialises the internal random reliably
        sets internal values correctly
    """)
    def __init__(
            self,
            lock: mp.Lock,
            parameters: Optional[str] = None
    ) -> None:
        """
        :param lock:        A single lock shared by all Predictors in
                            each Period for this invocation. Stored in
                            ``self.lock``.
        :type lock:         multiprocessing.Lock

        :param parameters:  The parameters passed in by
                            ``hokohoko.Hokohoko.Config.predictor_parameters``.
                            Stored in ``self.parameters``.
        :type parameters:   str

        **Other Attributes:**

            .. code-block:: Text

                symbol_ids      [numpy.ndarray] The list of symbols
                                available in the data source.

                account         [hokohoko.entities.Account] The internal
                                account keeping track of state.

        **Deterministic RNG:**

            In order that successive runs of Hokohoko with identical
            settings and data generate the exact same results, the
            Predictor class inherits from ``random.Random`` to provide a
            fully deterministic RNG. For any specific minute within the
            dataset, the generated random number sequence should be
            identical.

            The RNG should typically be accessed via ``self.random()``
            or ``self.randint()``.

            See `random <https://docs.python.org/3/library/random.html>`_
            for additional methods.

        """
        super().__init__(self)
        self.parameters = parameters
        self.lock = lock
        self.symbol_ids = []
        self.account = Account()
        self._order_id = 0

    def __new__(
            cls,
            lock: mp.Lock,
            parameters: Optional[str] = None,
    ) -> None:
        """
        Override because of Random mixing __init__ and __new__. (Is this
        a pre-3.8 thing, or a windows cPython thing, or what?)

        :param lock:
        :param parameters:
        :return:
        """
        # TODO: Ensure this works with 3.7 AND 3.8.
        return Random.__new__(cls, Predictor._MAGIC_SEED)

    def __enter__(self) -> 'Predictor':
        """
        Any state required for the predictor should be setup in here,
        e.g., external data sources.

        :returns:       As per `with` specification, ``self``.
        :rtype:         hokohoko.entities.Predictor

        .. include:: must_override.rst

        """
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up the predictor state, close and release handles, etc.

        .. include:: must_override.rst

        """
        raise NotImplementedError

    def on_start(self, bars: Iterable[Bar]) -> None:
        """
        This is called when the predictor is first loaded. The order of
        the symbols within the list doesn't change for the duration of
        the test.

        :param bars:    A bar containing the closing values of the bar
                        prior to the Period the Predictor is running.
        :type bars:     list[hokohoko.entities.Bar]

        .. include:: must_override.rst

        """
        raise NotImplementedError

    def on_bar(self, bars: Iterable[Bar]) -> None:
        """
        This is called at the end of every bar, and is where the
        majority of a Predictor's work takes place. During this method,
        Orders and Positions can be requested closed, and Orders can be
        placed, but none are actioned until after this routine exits.
        Upon exit, ``close_order`` requests are handled first, then
        ``place_order[s]``.

        ``on_bar`` is considered to happen between the end of one bar,
        and the start of the next.

        :param bars:    The latest bar in the data.
        :type bars:     list[hokohoko.entities.Bar]

        .. include:: must_override.rst

        """
        raise NotImplementedError

    def on_stop(self) -> None:
        """
        This is called at the end of each period. It may be overridden,
        otherwise does nothing.
        """
        pass

# Account functions. ===================================================
    @utils.generate_tests("places order into orders")
    def place_order(self, order: Order) -> None:
        """
        Place a single Order into the market.

        :param order:   The desired Order.
        :type order:    hokohoko.entities.Order

        """
        self.account.orders[self._order_id] = order
        self._order_id += 1

    @utils.generate_tests("""places all orders into orders""")
    def place_orders(self, orders: Iterable[Order]) -> None:
        """
        Place a collection of Orders into the market.

        :param orders:  A list of Orders to add to the orders stack.
        :type orders:   list[hokohoko.entities.Order]

        """
        for o in orders:
            self.place_order(o)
