import pytest
import json
import random


from .dummy import Dummy
from .string import String
from .boolean import Boolean
from .integer import Integer
from .number import Number
from .util import _test_valid_args, _test_invalid_args, Values, Value


class Json(Dummy):
    def __init__(self, max_depth: int = 2,
                 lists: bool = True, dicts: bool = True,
                 strings: bool = True, booleans: bool = True,
                 integers: bool = True, numbers: bool = True,
                 nulls: bool = True):
        super().__init__()
        self.max_depth = max_depth
        self.lists = lists
        self.dicts = dicts
        self.strings = strings
        self.booleans = booleans
        self.integers = integers
        self.numbers = numbers
        self.nulls = nulls

    def valid(self, value, raise_error=False):
        try:
            json.loads(value)
            return True
        except json.decoder.JSONDecodeError as e:
            if raise_error:
                raise ValueError("{} is not a valid json string: {}".format(
                    value, e
                ))
            return False

    def _data(self, depth):
        if depth == 0:
            return {}
        data = {
            **({"list_value": [
                *([self._data(depth - 1)] if self.dicts else []),
                *([String().valids()[0]] if self.strings else []),
                *([Boolean().valids()[0]] if self.booleans else []),
                *([Integer().valids()[0]] if self.integers else []),
                *([Number().valids()[0]] if self.numbers else []),
                *([None] if self.nulls else []),
            ]} if self.lists else {}),
            **({"dict_value": self._data(depth - 1)} if self.dicts else {}),
            **({"string_value": String().valids()[0]} if self.strings else {}),
            **({"boolean_value": Boolean().valids()[0]} if self.booleans else {}),
            **({"integer_value": Integer().valids()[0]} if self.integers else {}),
            **({"number_value": Number().valids()[0]} if self.numbers else {}),
            **({"null_value": None} if self.nulls else {}),
        }
        return data

    def _valids(self):
        return Value(json.dumps(self._data(self.max_depth)))

    def _invalids(self):
        invalids = [
            Integer().valids()[0],
            Number().valids()[0],
            String().valids()[0],
        ]
        return Values(invalids)

    def __str__(self):
        config = {
            "lists": self.lists,
            "dicts": self.dicts,
            "strings": self.strings,
            "booleans": self.booleans,
            "integers": self.integers,
            "numbers": self.numbers,
            "nulls": self.nulls,
        }
        config = [
            k for k, v in config.items()
            if v
        ]
        return "Json: {}, {}".format(self.max_depth, config)


def test_json():
    _test_valid_args(Json, [
        [], [2],
        {
            "max_depth": 4,
        },
        {
            "lists": True,
            "dicts": False,
            "strings": False,
            "booleans": False,
            "integers": False,
            "numbers": False,
            "nulls": False,
        }
    ])

    _test_invalid_args(Json, [
        {"x": True}
    ])

    for max_depth in range(5):
        json.loads(Json(max_depth).valids()[0])
    assert {} == json.loads(Json(0).valids()[0])
    assert {} == json.loads(Json(0, *[False for i in range(7)]).valids()[0])
    for i in range(8):
        assert 7 - \
            i == len(json.loads(
                Json(1, *[False for i in range(i)]).valids()[0]))
