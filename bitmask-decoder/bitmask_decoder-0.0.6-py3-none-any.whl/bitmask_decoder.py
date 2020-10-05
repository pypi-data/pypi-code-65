""" This module is to decode a bitmask for weekdays.

This mask is created by assigning an integer to each day of the week and summing up the integers of the relevant days.

It is assumed that the days are assigned as follows:

Monday: 1
Tuesday: 2
Wednesday: 4
Thursday: 8
Friday: 16
Saturday: 32
Sunday: 64
Any combinations of these days can be summed up to create a mask for that specific combination. For example:

42 = Tuesday(2), Thursday(8) and Saturday(32)
17 = Monday (1), Friday (16)

"""

import itertools
import numpy as np
import re
import warnings

weekdays = [1, 2, 4, 8, 16, 32, 64]

weekday_mapping = {
    1: "Mon",
    2: "Tue",
    4: "Wed",
    8: "Thu",
    16: "Fri",
    32: "Sat",
    64: "Sun"
}

def decode_weekday(bitcode):
    """
    Decode a bitcode to a list of weekdays.

    Parameters
    ----------
    bitcode : [int]
        bitcode int e.g. 127 for all week days
    """
    try:
        bitcode = int(bitcode)
    except ValueError:
        return np.nan

    combinations = [seq for i in range(len(weekdays), 0, -1) for seq in itertools.combinations(weekdays, i) if
                    sum(seq) == bitcode]

    # If correct, it should only return one combination.
    try:
        combination = combinations[0]
    except IndexError:  # No combinations found
        return

    result = [weekday_mapping[x] for x in combination]

    return result


def decode_all_weekdays(bitcode_list):
    """
    Decode a list of bitcode to a list of lists of weekdays
    
    Parameters
    ----------
    bitcode_list : [list[int]]
        list of bitcode ints e.g. [42, 127]
    """
    result = [decode_weekday(bitcode) for bitcode in bitcode_list]
    
    return result

def encode_weekday(weekday_list):
    """
    Encode a list of weekdays to a list of bitcode
    
    Parameters
    ----------
    weekday_list : [list[str]]
        list of weekday strings e.g. ["Mon", "Fri"]
    """
    regex = {
    "Mon" : re.compile(r"(Mo(n(day)?)?|0|Ma(a(ndag)?)?)"),
    "Tue" : re.compile(r"(Tu(e(sday)?)?|1|Di(n(sdag)?)?)"),
    "Wed" : re.compile(r"(We(d(nesday)?)?|2|Wo(e(nsdag)?)?)"),
    "Thu" : re.compile(r"(Th(u(rsday)?)?|3|Do(n(derdag)?)?)"),
    "Fri" : re.compile(r"(Fr(i(day)?)?|4|Vr(ij(dag)?)?)"),
    "Sat" : re.compile(r"(Sa(t(urday)?)?|5|Za(t(erdag)?)?)"),
    "Sun" : re.compile(r"(Su(n(day)?)?|6|Zo(n(dag)?)?)")
    }
    
    encoded = []
    for day in weekday_list:
        for key in regex:
            if (regex[key].match(str(day).capitalize())) is not None:
                encoded.append(list(weekday_mapping.keys())[list(weekday_mapping.values()).index(key)])

    if len(encoded) < len(weekday_list):
        warnings.warn('Warning: not all days could be interpreted')
        return np.nan
    else:
        result = sum(encoded)
        return result


def encode_all_weekdays(all_weekday_list):
    """
    Encode a list of lists of weekdays to a list of lists of bitcode
    
    Parameters
    ----------
    all_weekday_list : [list[list[str]]]
        list of lists of weekday strings e.g. [["Mon", "Fri"], ["Sat", "Sun"]]
    """
    result = [encode_weekday(weekdays) for weekdays in all_weekday_list]
    
    return result
