# -*- coding: utf-8 -*-
#
# system utilities methods
# IMIO <support@imio.be>
#

from collections import OrderedDict

# ------------------------------------------------------------------------------


def insert_in_ordereddict(dic, value, after_key='', at_position=None):
    """
        Insert a tuple in an new Ordereddict.
        :param dic: the original OrderedDict
        :param value: a tuple (key, value) that will be added at correct position
        :param after_key: key name after which the tup is added
        :param at_position: position at which the tup is added. Is also a default if after_key is not found
        :return: a new OrderedDict or None if insertion position is undefined
    """
    position = None
    if after_key is not None:
        keys = dic.keys()
        if after_key in keys:
            position = keys.index(after_key) + 1
    if position is None and at_position is not None:
        position = at_position
    if position is None:
        return None
    if position >= len(dic.keys()):
        return OrderedDict(dic.items() + [value])
    tuples = []
    for i, tup in enumerate(dic.items()):
        if i == position:
            tuples.append(value)
        tuples.append(tup)
    if not tuples:  # dic was empty
        tuples.append(value)
    return OrderedDict(tuples)
