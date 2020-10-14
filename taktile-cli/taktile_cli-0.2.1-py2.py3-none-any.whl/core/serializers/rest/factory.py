from collections.abc import Sequence
from functools import singledispatch
from typing import List, Union

import numpy
import pandas

from tktl.core.loggers import CliLogger
from tktl.core.serializers import rest
from tktl.core.serializers.base import CustomDeserializingModelT

logger = CliLogger()


def deserialize_rest(
    model_input: Union[List[CustomDeserializingModelT], CustomDeserializingModelT]
):
    if isinstance(model_input, list):
        return [v.deserialize() for v in model_input]
    else:
        return model_input.deserialize()


@singledispatch
def serialize_rest(model_input):
    return model_input


@serialize_rest.register
def _(model_input: Sequence):
    return rest.SequenceSerializer.serialize(value=model_input)


@serialize_rest.register(dict)
def _(model_input):
    return rest.SequenceSerializer.serialize(value=model_input)


@serialize_rest.register
def _(model_input: numpy.ndarray):
    return rest.ArraySerializer.serialize(value=model_input)


@serialize_rest.register
def _(model_input: pandas.DataFrame):
    return rest.DataFrameSerializer.serialize(value=model_input)


@serialize_rest.register
def _(model_input: pandas.Series):
    return rest.SeriesSerializer.serialize(value=model_input)
