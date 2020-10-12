#   hokohoko/hokohoko.py
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
#   This is the main file for Hokohoko.
#

"""
========
Hokohoko
========

This is the base module for Hokohoko. Can be invoked either
programmatically by passing an appropriately configured
``hokohoko.Hokohoko.Config`` to ``hokohoko.Hokohoko.run()``, or
by invoking in a script:

.. code-block :: Text

    python3 -m hokohoko.Hokohoko [options]


Several options are available however to ease testing and debugging
during Predictor development, so feel free to explore the options and
associated documentation. However, for benchmarking, the only ones you
should need to change are:

.. code-block :: Text

    predictor       Should be set to your Predictor of choice (which
                    inherits hokohoko.entities.Predictor), along with
                    any required parameters.
    process_count   Tune for how many cores you are willing to use.
                    Hokohoko uses roughly 1GB of RAM, plus the
                    Predictor's internal state, per core.

and:

.. code-block :: Text

    assessor    The assessor class you wish to use, plus its parameters.
                Multiple assessors can be defined.

.. note::
    The default options have been tuned from analysis of over 1000
    peer-reviewed papers' settings. If you do feel the need to use
    custom settings, please make sure you record them with your results,
    so others can compare their work with yours.

"""
import cProfile
import multiprocessing as mp
import sys
from argparse import ArgumentParser
from datetime import datetime
from timeit import default_timer
from typing import Iterable, List, Tuple

import numpy as np

from hokohoko import _run, defaults, utils
from hokohoko._period import Period, PeriodConfig
from hokohoko.entities import Account, Config


@utils.generate_tests("""
    returns a HokohokoConfig.
    defaults are set correctly.
""")
def _make_config_from_arguments() -> Config:
    """
    Parses command-line arguments.

    :returns:   The Config.
    :rtype:     hokohoko.entities.Config
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-P", "--predictor",
        help="Predictor to use, plus configuration string.",
        type=str,
        default=defaults.DEFAULT_PREDICTOR_CLASS
    )
    parser.add_argument(
        "-A", "--assessor",
        help="Assessor to use, plus configuration string.",
        type=str, action='append',
        default=defaults.DEFAULT_ASSESSORS
    )
    parser.add_argument(
        "-D", "--data",
        help="Data Source to use, plus configuration string.",
        type=str,
        default=defaults.DEFAULT_DATA
    )
    parser.add_argument(
        "-S", "--subset",
        help="Symbol subset to use. Comma separated codes, e.g. 'AUDUSD,AUDNZD'.",
        type=str,
        default=defaults.DEFAULT_DATA_SUBSET
    )
    parser.add_argument(
        "-n", "--period-number",
        help="The number of Periods for testing.",
        type=int,
        default=defaults.DEFAULT_PERIOD_COUNT
    )
    parser.add_argument(
        "-c", "--process-count",
        help="Number of concurrent processes to use.",
        type=int,
        default=defaults.DEFAULT_PROCESS_COUNT
    )
    parser.add_argument(
        "-f", "--past-minutes",
        help="How many minutes in each Bar (f=from).",
        type=int,
        default=defaults.DEFAULT_PAST_MINUTES
    )
    parser.add_argument(
        "-t", "--hold-minutes",
        help="How many future minutes to evaluate a Position for (t=to).",
        type=int,
        default=defaults.DEFAULT_HOLD_MINUTES
    )
    parser.add_argument(
        "--load-limit",
        help="Limit number of data rows.",
        type=int,
        default=defaults.DEFAULT_LOAD_LIMIT
    )
    parser.add_argument(
        "--training-minutes",
        help="Override training size (for testing only).",
        type=int,
        default=defaults.DEFAULT_TRAINING_MINUTES
    )
    parser.add_argument(
        "--test-minutes",
        help="Override test size (for testing only).",
        type=int,
        default=defaults.DEFAULT_TEST_MINUTES
    )
    parser.add_argument(
        "--profiling",
        help="Enable profiling out (files will be called 'profile_[period_id]')",
        action='store_true'
    )

    args = parser.parse_args()

    return Config(
        predictor_class=args.predictor,
        assessors=args.assessor,
        data_class=args.data.split(maxsplit=1)[0],
        data_parameters=args.data.split(maxsplit=1)[1],
        data_subset=args.subset,
        period_count=args.period_number,
        process_count=args.process_count,
        past_minutes=args.past_minutes,
        hold_minutes=args.hold_minutes,
        load_limit=args.load_limit,
        training_minutes=args.training_minutes,
        test_minutes=args.test_minutes,
        profiling=args.profiling
    )


@utils.generate_tests("""
    returns the correct number of periods.
    if possible, the periods are the correct length.
    training, testing and hold periods are correct.
    raises an error if the settings don't work on the given data source.
    returns an iterable of PeriodConfigs.
    all PeriodConfigs are unique.
    doesn't over-saturate.
    periods include the available symbols.
    respects load_limit if possible.
""")
def _calculate_periods(
        minutes: int,
        config: Config,
        available_symbols: np.ndarray
) -> List[PeriodConfig]:
    """
    Generates a list of tuples that can be passed into a Period. A full
    period consists of a test period plus training period, with
    hold_minutes left at the end to give all benchmarked Positions fair
    consideration.

    :param minutes: How many minutes are available from the data source.
    :type minutes:  int

    :param config:  The config parameters provided to this benchmark.
    :type config:   hokohoko.entities.Config

    :returns:       A list of Period.Config configuration options.
    :rtype:         Iterable[hokohoko._period.PeriodConfig]

    """
    if config.load_limit is not None:
        minutes = min(minutes, config.load_limit)

    # Allow for overlap at both ends.
    period_length = (config.past_minutes +
                     config.training_minutes +
                     config.test_minutes +
                     config.hold_minutes)

    # Prevent duplicates in the event of saturation.
    if minutes - period_length < config.period_count:
        period_count = minutes - period_length + 1
    else:
        period_count = config.period_count

    step = int((minutes - period_length) / period_count)
    offset = int(step / 2) + config.past_minutes
    return [
        PeriodConfig(
            i,
            i * step + offset,
            i * step + config.training_minutes + offset,
            i * step + period_length + offset,
            available_symbols
        )
        for i in range(period_count)
    ]


@utils.generate_tests("""
    returns an account
    generates profiles if configured.
""")
def _process(
        shared_config: Config,
        config: PeriodConfig
) -> Tuple[int, Account]:
    """
    Runs a Period with the given configuration.

    :param shared_config:   Global configuration options.
    :type shared_config:    hokohoko.entities.Config

    :param config:          Per-Period configuration options.
    :type config:           hokohoko._period.PeriodConfig

    :return:                The simulated Account histories, per-Period.
    :rtype:                 Tuple[int, hokohoko.entities.Account]
    """
    period = Period()

    if not shared_config.profiling:
        account = _run.run(period, shared_config, config)
    else:
        prof = cProfile.Profile()
        account = prof.runcall(_run.run, period, shared_config, config)
        prof.dump_stats(f'profile_simulate_{config.period_id: 03d}')
    return config.period_id, account


@utils.generate_tests("""
    a known benchmark with --debug produces an account with known results.
    a known simulation with --debug produces an account with known results.
""")
def run(config: Config) -> None:
    """
    Runs the Hokohoko benchmark suite based on the provided config.

    :param config:  The global configuration options.
    :type config:   hokohoko.Hokohoko.HokohokoConfig
    """
    # 0. Housekeeping.
    if mp.get_start_method(True) is None:
        mp.set_start_method('spawn')

    if __debug__:
        print(config)
    start_time = default_timer()
    assessors = []
    for a in config.assessors:
        a_name, a_parameters = utils.split_class_options(a)
        assessors.append(utils.get_fq_class(a_name)(a_parameters))

    # 1. Build per-process configuration options. To do this, we need to
    #    know the source length.
    with utils.get_fq_class(config.data_class)(
            config.data_parameters, None, load=False
    ) as data:
        period_configs = _calculate_periods(data.get_minutes(), config, data.get_symbol_ids())

    # 2. Run the processes.
    with mp.Pool(
        processes=config.process_count,
        initializer=Period.init,
        initargs=(mp.Lock(), mp.Lock())
    ) as pool:
        accounts = [pool.apply_async(_process, args=[config, pc]) for pc in period_configs]
        pool.close()
        pool.join()

    # 3. Analyse the trace.
    for a in assessors:
        a.analyse(accounts)

    end_time = default_timer()
    print(f"Finished in {end_time - start_time: .1f} seconds at {datetime.now()}.")


if __name__ == "__main__":
    _config = _make_config_from_arguments()
    run(_config)
    sys.exit()
