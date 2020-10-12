#   hokohoko/utils.py
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
#   This module contains a selection of utility functions used by
#   Hokohoko.
#

"""
=====
utils
=====
"""
from importlib import import_module
from typing import Optional

import numpy as np


def generate_tests(descriptions):
    """
    A decorator class that allows tests to be prescribed locally.

    :param descriptions:    Test cases to generate. Should be one test
                            case per line.
    :type descriptions:     str

    :return:    The decorated function.
    :rtype:     function
    """
    def decorate(f):
        setattr(f, '__hokohoko_test_cases__', descriptions)
        return f
    return decorate


@generate_tests("""
    raises an error it it can't access the module
    raises an error if it can't access the class
    accepts single-hierarchy class
    accepts fully qualified class
    returns the correct class
""")
def get_fq_class(fq_class) -> callable:
    """
    Creates a reference to a class from a fully qualified class name.
    This reference can then be used to instantiate the class.

    :param fq_class:    The fully-qualified name of the class. E.g.
                        'hokohoko.predictors.DoNothing'.
    :type fq_class:     str

    :returns:           The class which may then be instantiated.
    :rtype:             callable
    """
    temp = fq_class.rsplit(".", 1)
    if len(temp) == 2:
        module_name, name = temp
    else:
        module_name, name = temp[0], temp[0]
    module = import_module(module_name)
    return getattr(module, name)


@generate_tests("""
    raises an error on empty symbol
    raises an error if symbol is not string
    returns a numpy.int64
    returns the correct value
""")
def convert_symbol_to_id(symbol: str) -> np.int64:
    """
    Converts a symbol/currency pair name into an integer representation.

    :param symbol:  The symbol/currency pair name to convert.
    :type symbol:   str

    :returns:       An integer value for the symbol/currency pair name.
    :rtype:         numpy.int64
    """
    if symbol is None or len(symbol) == 0:
        raise ValueError(f"Cannot convert empty symbol: {symbol}")

    return np.int64(int.from_bytes(symbol.encode('ascii'), 'big'))


@generate_tests("""
    raises an error if not provided a number
    returns a string
    returns the correct string
""")
def convert_id_to_symbol(symbol_id: np.int64) -> str:
    """
    Converts an integer to a symbol/currency pair name.

    :param symbol_id:   The integer value to convert.
    :type symbol_id:    numpy.int64

    :returns:           The symbol/currency pair name from the integer.
    :rtype:             str
    """
    return symbol_id.item().to_bytes(8, 'big').decode('ascii').strip('\x00')


@generate_tests("""
    raises an error if not provided an array
    returns a dictionary of tuples.
    all symbols are mapped to their own index
    symbols that are base currency already map to themselves
    symbols map to the correct base pair
    symbols map to the correct reversed base pair
    symbols that don't have a base connection map to None
    the base currency gets changed correctly
""")
def generate_currency_map(symbol_ids: np.ndarray, base: Optional[str] = "USD") -> dict:
    """
    Calculates the chain for each base currency to USD. Each item in the
    dictionary is a tuple which, if followed in order, will calculate
    the currencies conversion to USD. If the Tuple is None, it cannot be
    used by Hokohoko, and will be ignored if requested.

    .. note::
        This assumes there is a single direct currency pair available.
        It makes no attempt to build chains.

    :param symbol_ids:  The set of IDs available from the data source.
    :type symbol_ids:   numpy.ndarray<numpy.int64>

    :param base:        The currency to use as a base.
    :type base:         str

    :returns:           A dictionary mapping symbol_ids to their index,
                        and the currency pair required to convert
                        Account currency to the symbol's currency pair,
                        or None if not available.
    :rtype:             dict<numpy.int64: tuple<int, Union[numpy.int64, None]>

    """
    base_id = convert_symbol_to_id(base)

    results = {}
    for i, symbol_pair in enumerate(symbol_ids):
        a = symbol_pair >> 24
        b = symbol_pair & 0xFFFFFF

        if a == base_id or b == base_id:
            # results[i] = i
            results[symbol_pair] = (i, symbol_pair, symbol_pair)
        else:
            found_base = None
            found_target = None
            for j, target in enumerate(symbol_ids):
                c = target & 0xFFFFFF
                d = target >> 24

                if (c == a and d == base_id) or (c == base_id and d == a):
                    found_base = target
                if (c == b and d == base_id) or (c == base_id and d == b):
                    found_target = target

            results[symbol_pair] = (i, found_base, found_target)

    return results


def split_class_options(class_options: str):
    """
    Splits a class name from its options.

    :param class_options:   The class name and options as a single string.
    :type class_options:    str

    :returns:   The class and options, joint.
    :rtype:     Tuple[str, Union[None, str]]
    """
    c_o = class_options.split(maxsplit=1)
    c_name = c_o[0]
    if len(c_o) > 1:
        c_parameters = c_o[1]
    else:
        c_parameters = None

    return c_name, c_parameters
