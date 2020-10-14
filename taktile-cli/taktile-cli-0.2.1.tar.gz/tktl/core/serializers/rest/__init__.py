import json
from collections import OrderedDict
from typing import Any, Dict, List, Sequence, Union

import numpy
import pandas
from pandas.core.dtypes.inference import is_sequence

from tktl.core.serializers.base import CustomDeserializingModelT, ObjectSerializer


class DataFrameSerializer(ObjectSerializer):
    @classmethod
    def deserialize(cls, value: CustomDeserializingModelT) -> pandas.DataFrame:
        return value.deserialize()

    @classmethod
    def serialize(cls, value: pandas.DataFrame) -> List[Dict]:
        return value.to_dict("records", into=OrderedDict)


class SeriesSerializer(ObjectSerializer):
    @classmethod
    def deserialize(cls, value: CustomDeserializingModelT) -> pandas.DataFrame:
        return value.deserialize()

    @classmethod
    def serialize(cls, value: pandas.Series) -> Dict:
        if not value.name:
            value.name = "Series"
        return {value.name: value.tolist()}


class ArraySerializer(ObjectSerializer):
    @classmethod
    def deserialize(cls, value: CustomDeserializingModelT) -> pandas.DataFrame:
        return value.deserialize()

    @classmethod
    def serialize(cls, value: numpy.ndarray) -> Dict:
        return {"value": json.dumps(value.tolist())}


class SequenceSerializer(ObjectSerializer):
    @classmethod
    def deserialize(
        cls, value: Union[List[CustomDeserializingModelT], CustomDeserializingModelT]
    ) -> Any:
        return value

    @classmethod
    def serialize(cls, value: Sequence) -> Union[Dict, List[Dict]]:
        if isinstance(value, dict):
            return value
        elif isinstance(value, list):
            if len(value) > 0:
                first = value[0]
                if isinstance(first, list):
                    return {"value": json.dumps(value)}
                elif isinstance(first, dict):
                    return value
                elif not is_sequence(first):
                    return value
            else:
                raise ValueError("Input must be non-empty")
        else:
            raise ValueError("Invalid inputs provided")
