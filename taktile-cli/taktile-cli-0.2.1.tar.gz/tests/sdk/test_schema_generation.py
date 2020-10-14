import json
from typing import List, Type

import numpy
import pandas
import pandas.api.types as ptypes
from tktl.core.serializers.rest.typed import to_pydantic


def test_from_single_value():
    schema = to_pydantic(342314)
    assert schema.__name__ == "SingleValue"
    assert schema.validate({"inputs": 1})
    deser = schema(**{"inputs": 1}).deserialize()
    assert deser == 1


def test_from_series(serializer_df_inputs: pandas.DataFrame):
    series = serializer_df_inputs.A
    schema = to_pydantic(series)
    assert schema.__name__ == "Series"
    rand_values = {"A": [1, 1, 12, 1, 1, 321, None]}
    assert schema.validate(rand_values)
    deser = schema(**rand_values).deserialize()
    assert isinstance(deser, pandas.Series)
    assert ptypes.is_float_dtype(deser.dtype)


def test_from_frame(serializer_df_inputs: pandas.DataFrame):
    schema = to_pydantic(serializer_df_inputs)
    assert schema.__name__ == "DataFrame"
    rand_values = {k: [1, 2, 3] for k in serializer_df_inputs.columns}
    assert schema.validate(rand_values)
    deser = schema(**rand_values).deserialize()
    assert isinstance(deser, pandas.DataFrame)
    for col in deser.columns:
        assert ptypes.is_float_dtype(deser[col].dtype)


def test_from_array():
    arr = numpy.random.randn(100)
    schema = to_pydantic(arr)
    assert schema.__name__ == "Array"
    rand_values = {
        "values": json.dumps(numpy.array([1, 1, 12, 1, 1, 321, None]).tolist())
    }
    assert schema.validate(rand_values)
    print(schema.validate(rand_values))
    deser = schema(**rand_values).deserialize()
    assert isinstance(deser, numpy.ndarray)


def test_from_sequence():
    sequence = [1, 2, None, 4, 2, 1e10, 1.2]
    schema = to_pydantic(sequence)
    assert schema == List[int]

    sequence = [[1], [2], [None], [4, 2, 1e10, 1.2]]
    schema = to_pydantic(sequence)
    assert schema == List[List[int]]

    sequence = [{"a": 1, "b": 2}, {"a": 1, "b": 100}]
    to_pydantic(sequence)
