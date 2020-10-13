import pytest


from .dummy import Dummy
from .util import _test_valid_args, _test_invalid_args, Values


class Boolean(Dummy):
    def __init__(self, *invalids):
        super().__init__()
        if len(invalids) != len(set(invalids)):
            raise ValueError("invalids must be unique.")
        for invalid in invalids:
            if not isinstance(invalid, bool):
                raise ValueError("{} is not a boolean but a {}.".format(
                    value, type(value)
                ))
        if len(invalids) == 0:
            valids = [True, False]
        elif len(invalids) == 1:
            valids = [not invalids[0]]
        else:
            valids = []
        self._valids_ = valids
        self._invalids_ = invalids

    def _valids(self):
        return Values(self._valids_)

    def _invalids(self):
        return Values(self._invalids_)

    def valid(self, value, raise_error=False):
        if not isinstance(value, bool):
            if raise_error:
                raise ValueError("{} is not of type bool but {}".format(
                    value, type(value)
                ))
            return False
        if value not in self._valids_:
            if raise_error:
                raise ValueError("{} not a valid value, must be in {}".format(
                    value, self._valids_
                ))
            return False
        return True
    
    def __str__(self):
        return "Boolean: {} / {}".format(self._valids_, self._invalids_)


def test_boolean():
    _test_valid_args(Boolean, [
        [], [True], [False],
        [True, False], [False, True]
    ])

    _test_invalid_args(Boolean, [
        [False, False], [True, True],
        [True, False, True], [False, True, False],
        [True for i in range(3)]
    ])

    assert Boolean(False).valids() == [True]
    assert Boolean(False).invalids() == [False]
    assert Boolean(True).valids() == [False]
    assert Boolean(True).invalids() == [True]
    assert Boolean().valids(2) == [True, False]
    assert Boolean().invalids() == []
