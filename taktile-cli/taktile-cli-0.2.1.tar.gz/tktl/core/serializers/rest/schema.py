import json
from collections.abc import Sequence
from typing import Any, Dict, List, Type

import numpy
import pandas
from pydantic import BaseModel

from tktl.core.serializers.base import CustomDeserializingModelT


def get_single_value_model(value: Any):
    class SingleValueModel(CustomDeserializingModelT):
        inputs: type(value)

        def deserialize(self):
            return self.inputs

    return SingleValueModel


def get_dataframe_model(
    df: pandas.DataFrame, base_model: Type[BaseModel]
) -> Type[CustomDeserializingModelT]:
    class DataFrame(base_model, CustomDeserializingModelT):
        _columns = df.columns
        _dtypes = df.dtypes

        def deserialize(self):
            _df = pandas.DataFrame.from_dict(self.dict())
            _df = _df[self._columns]  # column order
            _df = _df.astype(self._dtypes)  # column types
            return _df

    return DataFrame


def get_series_model(
    series: pandas.Series, base_model: Type[BaseModel]
) -> Type[CustomDeserializingModelT]:
    class Series(base_model, CustomDeserializingModelT):
        _name = series.name
        _dtype = series.dtype

        def deserialize(self):
            values = self.dict()[self._name]
            _series = pandas.Series(values)
            _series = _series.astype(self._dtype)  # column types
            return _series

    return Series


def get_jsonable_encoder_sequence_model(
    base_model: Type[BaseModel],
) -> Type[CustomDeserializingModelT]:
    class JsonableEncoderModel(base_model, CustomDeserializingModelT):
        def deserialize(self):
            return json.loads(self.values)

    return JsonableEncoderModel


def get_sequence_model(base_model: Type[BaseModel]) -> Type[CustomDeserializingModelT]:
    class SequenceEncoderModel(base_model, CustomDeserializingModelT):
        __root__ = List[base_model]

        def deserialize(self):
            return self.dict()

    return SequenceEncoderModel


def get_recursively_maybe_jsonable_sequence_types(sequence: Sequence, types=None):
    # TODO: recursive type discovery
    first = sequence[0]
    types = [List] if not types else types
    if isinstance(first, Sequence):
        types.append(List)
        return get_recursively_maybe_jsonable_sequence_types(first, types=types)
    if isinstance(first, dict):
        mapping = Dict
        inner = []
        for k, v in first.items():
            if isinstance(v, Sequence):
                rec = get_recursively_maybe_jsonable_sequence_types(v, types=inner)
    else:
        types.append(Type[type(first)])
    return types


def get_array_model() -> Type[CustomDeserializingModelT]:
    class ArrayModel(CustomDeserializingModelT):
        values: str

        def deserialize(self):
            return numpy.array(json.loads(self.values))

    return ArrayModel
