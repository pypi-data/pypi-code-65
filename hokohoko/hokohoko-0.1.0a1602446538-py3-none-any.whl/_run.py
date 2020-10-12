#   hokohoko/_run.py
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
#   This file contains the engine that makes Hokohoko work.
#

from typing import Dict, List, Tuple, Union

import numpy as np

from hokohoko import utils
from hokohoko._period import Period, PeriodConfig, get_last_close_at_minute, get_past_minutes
from hokohoko.entities import Account, Config, Data, Direction, Order, Position, Predictor, Status


class _Locals:
    """
    This class is used to pass around all the variables needed to
    support simulation.
    """
    def __init__(
            self,
            graph: Dict[np.int64, Tuple[int, np.int64]],
            subset_filter: List[np.int64]
    ):
        self.graph = graph
        self.subset_filter = subset_filter
        self.usd = utils.convert_symbol_to_id("USD")


@utils.generate_tests("""
    raises an error if period is None
    raises an error if period is not a Period
    raises an error if shared_config is None
    raises an error if shared_config is not a HokohokoConfig
    raises an error if config is None
    raises an error if config is not a PeriodConfig
    returns an account
    the account contains the correct amount of histories
    the history is correct for known configurations
""")
def run(period: Period, shared_config: Config, config: PeriodConfig) -> Account:
    """
    Simulates trading for the specified period and requested symbols.

    :param period:          The Period instance to operate on. This is
                            necessary to inherit the shared locks.
    :type period:           hokohoko._period.Period

    :param shared_config:   Global settings.
    :type shared_config:    hokohoko.Hokohoko.HokohokoConfig

    :param config:          The config unique to this period.
    :type config:           hokohoko._period.PeriodConfig

    :returns:               The account from this Period.
    :rtype:                 hokohoko.entities.Account

    """
    if __debug__:
        print(f"Period: {config}")

    required_symbols = calculate_required_symbols(
        shared_config.data_subset, config.available_symbols
    )

    with utils.get_fq_class(shared_config.data_class)(
            shared_config.data_parameters,
            required_symbols,
            config.origin,
            config.end,
            period.data_lock
    ) as source:
        predictor_class, predictor_parameters = utils.split_class_options(
            shared_config.predictor_class
        )
        with utils.get_fq_class(predictor_class)(
                period.predictor_lock, predictor_parameters
        ) as predictor:
            print(f"Period {config.period_id: 3d} started.")
            # 1a. Keep a local copy of the subset for filtering.
            if shared_config.data_subset is not None:
                subset_filter = np.array(
                    [utils.convert_symbol_to_id(s) for s in shared_config.data_subset.split(',')],
                    np.int64
                )
            else:
                subset_filter = source.get_symbol_ids()

            # 1b. Initialize the local variables.
            _locals = _Locals(
                graph=utils.generate_currency_map(source.get_symbol_ids()),
                subset_filter=subset_filter
            )

            # 1c. Initialize the Predictor.
            predictor.seed(config.origin)
            predictor.account.symbol_ids.extend(subset_filter)
            opening = get_last_close_at_minute(source, config.origin, shared_config.past_minutes)
            predictor.on_start([o for o in opening if o.symbol_id in subset_filter])

            # 2. Cycle through every minute in the dataset, but only
            #    sends x past minutes to the predictor.
            for minute in range(
                    config.origin + shared_config.past_minutes,
                    config.end,
                    shared_config.past_minutes
            ):
                # 2A. Get the past data, and simulate it.
                if minute >= config.test_point:
                    timestamps, data = source.get_partial_data(
                        minute - shared_config.past_minutes - 1, minute
                    )
                    simulate(predictor, _locals, timestamps, data)

                    if __debug__:
                        print(f"\x1b[0;103mBalance: {predictor.account.balance[-1]}\tEquity: "
                              f"{predictor.account.equity[-1]}\tPositions: "
                              f"{len(predictor.account.positions)}\x1b[0m")

                # 2B. Get the past bar, and send it to the Predictor.
                if minute < config.end - shared_config.hold_minutes:
                    past = get_past_minutes(source, minute - shared_config.past_minutes, minute)
                    predictor.seed(config.origin + minute)
                    predictor.on_bar([p for p in past if p.symbol_id in subset_filter])

                    # 2Bi. Apply to the account.
                    if minute >= config.test_point:
                        sanitize_orders(predictor, _locals)
                        calculate_positions(source, predictor, shared_config, _locals, minute)

                # 2C. Always clear stale orders.
                predictor.account.orders.clear()

            predictor.on_stop()
            print(f"Period {config.period_id: 3d} finished.")

    return predictor.account


@utils.generate_tests("""
    raises an error if account is None
    raises an error if account is not an Account
    raises an error if _locals is None
    raises an error if _locals is not an Account
    raises an error if minute is None
    raises an error if minute is not a list
    raises an error if minute is empty
    raises an error if minute is not solely Bars.
    correctly closes positions if they closed last minute.
    correctly opens orders if they opened last minute.
    correctly closes positions if they closed between minutes.
    correctly opens orders if they opened between minutes.
""")
def simulate(
        predictor: Predictor,
        _locals: _Locals,
        timestamps: List[np.int64],
        data: List[np.float32]
) -> None:
    """
    Processes the given minute of Bar data. This routine controls the
    movement of Positions between orders, positions and results. It also
    keeps track of equity/balance changes. This also happens before
    {place,close}_orders can be called by the Predictor.

    :param predictor:   The Predictor associated with this Period.
    :type predictor:    hokohoko.entities.Predictor

    :param _locals:     The period-local variables.
    :type _locals:      _Locals

    :param timestamps:  List of timestamps in the next chunk about to be
                        processed. The first minute is the last minute
                        of the previous chunk.
    :type timestamps:   list[numpy.int64]

    :param data:        List of data in the next chunk about to be
                        processed. The first minute is the last minute
                        of the previous chunk.
    :type data:         list[numpy.float32]

    """
    for i in range(1, len(timestamps)):
        closed = []
        for p_id, p in predictor.account.positions.items():
            s_index = _locals.graph[p.order.symbol_id][0]

            # 1. Check for status changes between minutes.
            l_close = data[s_index][i * 5 - 2]
            zz = (range(i * 5, i * 5 + 4))   # Array index.
            if p.close_time <= timestamps[i]:
                status = Status.CLOSED if p.status == Status.OPEN else p.status
                close_position(p, timestamps[i], data[:, zz], _locals, status, 0, p_id)
                closed.append(p_id)
                break

            t_open, t_high, t_low, t_close = data[s_index][zz]
            if p.status == Status.PENDING:
                if (
                        p.order.open_bid is None or
                        l_close >= p.order.open_bid >= t_open or
                        l_close <= p.order.open_bid <= t_open
                ):
                    open_position(p, timestamps[i], data[:, zz], _locals, 0, p_id)
            if p.status == Status.OPEN:
                if (
                        p.order.take_profit is not None and (
                            l_close <= p.order.take_profit <= t_open or
                            l_close >= p.order.take_profit >= t_open
                        )
                ):
                    close_position(
                        p,
                        timestamps[i],
                        data[:, zz],
                        _locals,
                        Status.CLOSED_TAKE_PROFIT,
                        0,
                        p_id
                    )
                    closed.append(p_id)
                    break
                elif (
                        p.order.stop_loss is not None and (
                            l_close <= p.order.stop_loss <= t_open or
                            l_close >= p.order.stop_loss >= t_open
                        )
                ):
                    close_position(
                        p,
                        timestamps[i],
                        data[:, zz],
                        _locals,
                        Status.CLOSED_STOP_LOSS,
                        0,
                        p_id
                    )
                    closed.append(p_id)
                    break

            # 2. Check for status changes within the minute.
            if p.status == Status.PENDING and t_low <= p.order.open_bid <= t_high:
                open_position(p, timestamps[i], data[:, zz], _locals, 1, p_id)
            if p.status == Status.OPEN:
                if p.order.take_profit is not None and t_low <= p.order.take_profit <= t_high:
                    close_position(
                        p,
                        timestamps[i],
                        data[:, zz],
                        _locals,
                        Status.CLOSED_TAKE_PROFIT,
                        1,
                        p_id
                    )
                    closed.append(p_id)
                    break
                elif p.order.stop_loss is not None and t_low <= p.order.stop_loss <= t_high:
                    close_position(
                        p,
                        timestamps[i],
                        data[:, zz],
                        _locals,
                        Status.CLOSED_STOP_LOSS,
                        1,
                        p_id
                    )
                    closed.append(p_id)
                    break

            # 3. Calculate the positions current value if still open.
            if p.status == Status.OPEN:
                calculate_final_value(p, data[:, zz], _locals, 2)

        # Effect closed positions.
        predictor.account.balance.append(predictor.account.balance[-1])
        for c in closed:
            p = predictor.account.positions.pop(c)
            predictor.account.balance[-1] += p.final_value - p.initial_value
            predictor.account.history[c] = p

        # Update equity here.
        predictor.account.equity.append(predictor.account.balance[-1])
        for p in predictor.account.positions.values():
            predictor.account.equity[-1] += p.final_value - p.initial_value

    # All positions need to be closed here.
    # for p_id, p in predictor.account.positions.items():
    #     s_index = _locals.graph[p.order.symbol_id][0]
    #     close_position(p, timestamps[i], data[:, zz], _locals, Status.CLOSED_STOP_LOSS, 1, p_id)
    #     p = predictor.account.positions.pop(c)
    #     predictor.account.balance[-1] += p.final_value - p.initial_value
    #     predictor.account.history[c] = p

    if __debug__:
        for p_id, p in predictor.account.positions.items():
            print("\tUpdated  {:8}: {}".format(p_id, p))


@utils.generate_tests("""
    raises an error if account is None
    raises an error if account is not an Account
    raises an error if position_id is None
    raises an error if position_id is not an int
    raises an error if position_id is less than 0
    raises an error if _locals is None
    raises an error if _locals is not a _Locals
    moves the position into account.positions
    removes the position from account.pending
    sets the pip value correctly
    sets the pip value correctly if JPY
""")
def open_position(position, timestamp, data, _locals, where, debug=None) -> None:
    """
    Open the Position.

    :param position:
    :param timestamp:
    :param data:
    :param _locals:
    :param where:       0 = Start, 1 = Middle
    :param debug:
    """
    position.status = Status.OPEN
    if where == 0:
        position.open_time = timestamp
        if position.order.open_bid is None:
            position.open_rate = data[_locals.graph[position.order.symbol_id][0]][0]
        else:
            position.open_rate = position.order.open_bid
    elif where == 1:
        position.open_time = timestamp + 30
        position.open_rate = position.order.open_bid
        if position.open_rate is None:
            raise ValueError("open_bid cannot be None in the middle of a Bar.")
    else:
        raise ValueError("open_position does not take where={}".format(where))
    position.initial_value = Account.POSITION_OPEN_VALUE
    position.final_value = Account.POSITION_OPEN_VALUE
    calculate_held_value(position, data, _locals, where)
    if __debug__ and debug is not None:
        print("\tOpened  {:8}: {}".format(debug, position))


@utils.generate_tests("""
    raises an error if account is None
    raises an error if account is not an Account
    raises an error if position_id is None
    raises an error if position_id is not an int
    raises an error if position_id is less than 0
    raises an error if position_id is not in account.positions
    raises an error if status is None
    raises an error if status is not a Status
    raises an error if _locals is None
    raises an error if _locals is not a _Locals
    creates a History in account.history for this position
    removes the position from account.positions
    adjusts account.balance correctly
""")
def close_position(position, timestamp, data, _locals, status, where, debug=None) -> None:
    """
    Close the Position. It will be transferred to history by the simulation routine.
    :param position:
    :param timestamp:
    :param data:
    :param _locals:
    :param status:
    :param where:       0 = Start, 1 = Middle
    :param debug:
    """
    position.status = status
    if where == 0:
        position.close_time = timestamp
        if status == Status.CLOSED_TAKE_PROFIT:
            position.close_rate = position.order.take_profit
        elif status == Status.CLOSED_STOP_LOSS:
            position.close_rate = position.order.stop_loss
        elif status == Status.CLOSED:
            position.close_rate = data[_locals.graph[position.order.symbol_id][0]][0]

    elif where == 1:
        position.close_time = timestamp + 30
        if status == Status.CLOSED_TAKE_PROFIT:
            position.close_rate = position.order.take_profit
        elif status == Status.CLOSED_STOP_LOSS:
            position.close_rate = position.order.stop_loss
        elif status == Status.CLOSED:
            position.close_rate = np.mean(data[_locals.graph[position.order.symbol_id][0]])

    else:
        raise ValueError("close_position does not take where={}".format(where))

    if position.status in (Status.CLOSED, Status.CLOSED_STOP_LOSS, Status.CLOSED_TAKE_PROFIT):
        calculate_final_value(position, data, _locals, where)
    if __debug__ and debug is not None:
        print("\tClosed   {:8}: {}".format(debug, position))


def calculate_held_value(position, data, _locals, where) -> None:
    """
    Calculate a Positions value from the initial_value.

    :param position:
    :param data:
    :param _locals:
    :param where:       0 = Start, 1 = Middle
    :return:
    """
    # 0. Safety
    if where not in (0, 1):
        raise ValueError("calculate_held_position does not support where={}".format(where))

    # 1. Need to calculate which values we need. This comes from the trade direction.
    s_index, base_symbol, target_symbol = _locals.graph[position.order.symbol_id]
    base_index, target_index = _locals.graph[base_symbol][0], _locals.graph[target_symbol][0]

    # 2. The exact calculation depends on the direction, and the ordering of the symbols.
    if position.order.direction == Direction.BUY:
        # 2A. Buy base through target.
        if base_index == target_index:
            account_rate = position.open_rate
        elif where == 0:
            account_rate = data[target_index][0]
        else:
            account_rate = np.mean(data[target_index])
        # Check for inversion
        if target_symbol & 0xFFFFFF == _locals.usd:
            account_rate = 1 / account_rate
        position.held_value = position.initial_value * account_rate / position.open_rate

    elif position.order.direction == Direction.SELL:
        # 2B. Buy target through base.
        if base_index == target_index:
            account_rate = position.open_rate
        elif where == 0:
            account_rate = data[base_index][0]
        else:
            account_rate = np.mean(data[base_index])
        # Check for inversion
        if base_symbol & 0xFFFFFF == _locals.usd:
            account_rate = 1 / account_rate
        position.held_value = position.initial_value * account_rate * position.open_rate


def calculate_final_value(position, data, _locals, where) -> None:
    """
    Calculates an account value (final_value) from the held value.

    :param position:
    :param data:
    :param _locals:
    :param where:       0 = Start, 1 = Middle, 2 = End
    :return:
    """
    # 0. Safety
    if where not in (0, 1, 2):
        raise ValueError("calculate_held_position does not support where={}".format(where))

    # 1. Need to calculate which values we need. This comes from the trade direction.
    s_index, base_symbol, target_symbol = _locals.graph[position.order.symbol_id]
    base_index, target_index = _locals.graph[base_symbol][0], _locals.graph[target_symbol][0]

    # 2. Calculate close_rate
    if position.close_rate > 0:
        close_rate = position.close_rate
    elif where == 0:
        close_rate = data[s_index][0]
    elif where == 1:
        close_rate = np.mean(data[s_index])
    else:
        close_rate = data[s_index][3]

    # 3. The exact calculation depends on the direction, and the ordering of the symbols.
    if position.order.direction == Direction.BUY:
        # 3A. Buy base through target.
        if base_index == target_index:
            account_rate = position.open_rate
        elif where == 0:
            account_rate = data[target_index][0]
        elif where == 1:
            account_rate = np.mean(data[target_index])
        else:
            account_rate = data[target_index][3]
        # Check for inversion
        if target_symbol & 0xFFFFFF == _locals.usd:
            account_rate = 1 / account_rate
        position.final_value = position.held_value * close_rate / account_rate

    elif position.order.direction == Direction.SELL:
        # 3B. Buy target through base.
        if base_index == target_index:
            account_rate = position.open_rate
        elif where == 0:
            account_rate = data[base_index][0]
        elif where == 1:
            account_rate = np.mean(data[base_index])
        else:
            account_rate = data[base_index][2]
        # Check for inversion
        if base_symbol & 0xFFFFFF == _locals.usd:
            account_rate = 1 / account_rate
        position.final_value = position.held_value / close_rate / account_rate


@utils.generate_tests("""
    raises an error if requested is None
    raises an error if requested is not a string
    raises an error if available is None
    raises an error if available is not a numpy.ndarray
    returns a string
    returns symbols which are their own base
    returns symbols which have a conversion available
    doesnt return symbols which have no conversion available
""")
def calculate_required_symbols(requested: str, available: np.ndarray) -> Union[None, str]:
    """
    Calculates the union of symbols requested with their conversion
    symbols if available. Filters out symbols that have no conversion
    available.

    :param requested:   The currencies requested.
    :type requested:    str

    :param available:   The currencies available in the data source.
    :type available:    numpy.ndarray[numpy.int64]

    :returns:           A comma-separated list of currencies to get.
    :rtype:             str

    """
    graph = utils.generate_currency_map(available)

    needed = {}
    if requested is None:
        return None
    else:
        for r in requested.split(","):
            sid = utils.convert_symbol_to_id(r)
            if sid in graph and graph[sid][1] is not None and graph[sid][2] is not None:
                needed[sid] = True
                needed[graph[sid][1]] = True
                needed[graph[sid][2]] = True

    return ",".join([utils.convert_id_to_symbol(n) for n in needed.keys()])


@utils.generate_tests("""
    raises an error if timestamps is None
    raises an error if timestamps is not a numpy array
    raises an error if timestamps is empty
    raises an error if data is None
    raises an error if data is not a numpy array
    raises an error if data is empty
    raises an error if graph is None
    raises an error if graph is empty
    raises an error if orders are None
    raises an error if orders are empty
    raises an error if orders are not all Orders
    raises an error if hold_minutes is negative
    raises an error if hold_minutes is 0
    raises an error if timestamp length is less than hold_minutes
    raises an error if data length is less than hold_minutes
    returns a List of Results
    returns a Result for every position
    calculates various conditions correctly.
""")
def calculate_positions(
        source: Data,
        predictor: Predictor,
        shared_config,
        _locals: _Locals,
        minute: int
) -> None:
    """
    Checks what happened to the given Order, within the period [minute, minute + hold_minutes).

    :param source:          The data source.
    :type source:           hokohoko.entities.Data

    :param predictor:       The predictor containing the account we are interested in.
    :type predictor:        hokohoko.entities.Predictor

    :param shared_config:   Globally-shared config options.
    :type shared_config:    hokohoko.HokohokoConfig

    :param _locals:         Period-local variables.
    :type _locals:          _Locals

    :param minute:          The index.
    :type minute:           int

    """
    future = get_past_minutes(source, minute, minute + shared_config.hold_minutes)
    for o_id, o in predictor.account.orders.items():
        f_index = _locals.graph[o.symbol_id][0]
        position = Position(
            order=o,
            future=future[f_index],
            status=Status.PENDING,
            open_time=future[f_index].start,
            close_time=future[f_index].end,
            open_rate=-1,               # These values will be over-written when required.
            close_rate=-1,              # As above.
            held_value=0.0,
            initial_value=0.0,
            final_value=0.0
        )
        # Must be convertible to account currency.
        if o.direction in (Direction.BUY, Direction.SELL):
            predictor.account.positions[o_id] = position
            if __debug__:
                print("\tOrdered  {:8}: {}".format(o_id, position))
        else:
            position.status = Status.NOT_TAKEN
            predictor.account.history[o_id] = position
            if __debug__:
                print("\tIgnored {:8}: {}".format(o_id, o))

    predictor.account.orders.clear()


@utils.generate_tests("""
    raises an error if subset_ids is absent
    raises an error if subset_ids is empty
    raises an error if subset_ids are not numpy.int64s
    raises an error if orders does not contain Orders only
    accepts an empty orders list
    accepts None for orders list
    returns a list of Orders
    doesn't remove multiple orders per symbol
    removes spurious don't orders
    adds all missing symbols and directions
    adds missing symbols once only
""")
def sanitize_orders(predictor: Predictor, _locals: _Locals) -> None:
    """
    Ensure the provided positions are appropriate for the requested symbol subset.

    :param predictor:   The Predictor associated with the current Period.
    :type predictor:    hokohoko.entities.Predictor

    :param _locals:     Variables local to the current Period.
    :type _locals:      _Locals

    """
    # 1. Mark if a symbol and direction combination has been seen.
    filtered = {s: [False, False] for s in _locals.subset_filter}
    for i, o in predictor.account.orders.items():
        if o.symbol_id in filtered:
            if o.direction in (Direction.BUY, Direction.DONT_BUY):
                filtered[o.symbol_id][0] = True
            if o.direction in (Direction.SELL, Direction.DONT_SELL):
                filtered[o.symbol_id][1] = True

    for s, f in filtered.items():
        if not f[0]:
            predictor.place_order(Order(s, Direction.DONT_BUY))
        if not f[1]:
            predictor.place_order(Order(s, Direction.DONT_SELL))
