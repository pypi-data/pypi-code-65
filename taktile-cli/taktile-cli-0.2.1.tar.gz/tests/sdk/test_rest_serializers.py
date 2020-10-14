import json
from collections import OrderedDict

import pandas
from tktl.core.serializers.rest import DataFrameSerializer, SeriesSerializer


def test_frame_serializer(serializer_df_inputs: pandas.DataFrame):
    as_pydantic_model = DataFrameSerializer.serialize(serializer_df_inputs)
    assert isinstance(as_pydantic_model, list)
    assert isinstance(as_pydantic_model[0], OrderedDict)
    assert list(as_pydantic_model[0].keys()) == serializer_df_inputs.columns.tolist()


def test_series_serializer(serializer_series_inputs: pandas.Series):
    as_pydantic_model = SeriesSerializer.serialize(serializer_series_inputs)
    assert isinstance(as_pydantic_model, dict)
    assert isinstance(as_pydantic_model["B"], list)
