from collections.abc import Sequence
from functools import singledispatch
from typing import Dict, List, Optional, Type, Union

import numpy
import pandas
from pandas.core.dtypes.inference import is_sequence
from pydantic import create_model

from tktl.core.serializers.base import CustomDeserializingModelT
from tktl.core.serializers.rest.schema import (
    get_array_model,
    get_dataframe_model,
    get_series_model,
    get_single_value_model,
)


@singledispatch
def to_pydantic(
    value, name: str = "SingleValue"
) -> Type[CustomDeserializingModelT]:  # noqa
    single_value_model = get_single_value_model(value=value)
    single_value_model.__name__ = name
    return single_value_model


@to_pydantic.register
def _(value: pandas.DataFrame, name: str = "DataFrame", nullable=True):
    """Create a Pydantic model for a batch from a Pandas DataFrame

    Parameters
    ----------
    value : pd.DataFrame
        Input Dataframe
    name : str, optional
        Name for the model, by default "DataFrame"
    nullable : bool, optional
        Indicates whether observations can be missing (None), by default True

    Returns
    -------
    ModelMetaclass
        Pydantic model of the dataframe
    """
    type_map = {}
    for col, values in value.to_dict().items():
        types = (type(v) for k, v in values.items() if v is not None)
        var_type = next(types, str)  # type of first item that is not None
        if nullable:
            var_type = Optional[var_type]
        type_map[col] = (List[var_type], None)

    DynamicBaseModel = create_model(name, **type_map)  # noqa
    return get_dataframe_model(base_model=DynamicBaseModel, df=value)


@to_pydantic.register
def _(value: pandas.Series, name: str = "Series"):
    """Create a Pydantic model for a batch from a Pandas Series

    Parameters
    ----------
    value : pd.Series
        Input Dataframe
    name : str, optional
        Name for the model, by default "DataFrame"
    nullable : bool, optional
        Indicates whether observations can be missing (None), by default True

    Returns
    -------
    ModelMetaclass
        Pydantic model of the series
    """
    nullable = True if value.isna().sum() > 0 else False
    type_name = "Series" if not value.name else value.name
    type_map = {}
    types = (type(v) for k, v in value.to_dict().items() if v is not None)
    var_type = next(types, str)  # type of first item that is not None
    if nullable:
        var_type = Optional[var_type]
    type_map[type_name] = (List[var_type], None)
    DynamicBaseModel = create_model(name, **type_map)  # noqa
    DynamicBaseModel.__name__ = name
    return get_series_model(series=value, base_model=DynamicBaseModel)


@to_pydantic.register
def _(value: numpy.ndarray, name: str = "Array"):
    """Create a Pydantic model for a batch from a Pandas Series

    Parameters
    ----------
    value : numpy.ndarray
    name : str, optional
        Name for the model, by default "DataFrame"

    Returns
    -------
    ModelMetaclass
        Pydantic model of the series
    """
    series_model = get_array_model()
    series_model.__name__ = name
    return series_model


@to_pydantic.register
def _(value: Sequence, name: str = "Sequence"):
    """Create a Pydantic model for a batch from a Pandas Series

    Parameters
    ----------
    value : Union[List, Dict]
        Input values, either Dict or List
    name : str, optional
        Name for the model, by default "DataFrame"

    Returns
    -------
    ModelMetaclass
        Pydantic model of the series
    """

    # TODO: instead of relying only on basic types, here we should instead be
    # able to see if inside each inner data structure there is a supported type (DataFrame, Series, ndarray, etc.)
    # generate schemas for those inner values
    if isinstance(value, list) or isinstance(value, tuple):
        if len(value) > 0:
            first = value[0]
            if isinstance(first, list):
                sequence_model = List[List[type(first[0])]]

            elif isinstance(first, dict):
                types = {k: (type(v), None) for k, v in first.items()}
                base_model = create_model(name, **types)
                sequence_model = List[base_model]
            # more specific than numpy's is_sequence implementation
            elif not is_sequence(first):
                sequence_model = List[type(first)]
            else:
                raise
        else:
            raise ValueError("Input must be non-empty")
    else:
        raise
    return sequence_model


@to_pydantic.register
def _(value: dict, name: str = "Dict"):
    types = {k: type(v) for k, v in value.items()}
    sequence_model = create_model(name, **types)  # noqa
    sequence_model.__name__ = name
    return sequence_model
