from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import Query
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
)
from pydantic import create_model


def to_pydantic(df, name="DataFrame", nullable=True):
    """Create a Pydantic model for a batch from a Pandas DataFrame

    Parameters
    ----------
    df : pd.DataFrame
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
    for col, values in df.to_dict().items():
        types = (type(v) for k, v in values.items() if v is not None)
        var_type = next(types, str)  # type of first item that is not None
        if nullable:
            var_type = Optional[var_type]
        type_map[col] = (List[var_type], Query(None))

    DynamicBaseModel = create_model(name, **type_map)

    class DataframeModel(DynamicBaseModel):
        _columns = df.columns
        _dtypes = df.dtypes

        def to_df(self):
            df = pd.DataFrame.from_dict(self.dict())
            df = df[self._columns]  # column order
            df = df.astype(self._dtypes)  # column types
            return df

    DataframeModel.__name__ = name
    return DataframeModel


def df_to_json_table(df, *args, **kwargs):
    """Create a json table from a pandas dataframe

    Parameters
    ----------
    df : pd.Dataframe
        Input dataframe
    *args: passed on to df.to_dict
    **kwargs: passed on to df.to_dict

    Returns
    -------
    string
        json encoded and versioned table
    """

    version = "tktl v0.1"

    string = df.to_json(*args, orient="split", **kwargs, index=False)

    return string[:-1] + ',"version":"' + version + '"}'


def df_to_dict(df):
    """Create a dictionary from pandas dataframes

    Types are converted to native Python types using pandas' built-in
    mapping (see pd.DataFrame.to_dict()).

    Parameters
    ----------
    df : pd.Dataframe
        Input dataframe

    Returns
    -------
    dict
        Dictionary with variable names as keys and columns as lists.
    """
    dataset = {}
    df = df.replace({np.nan: None})
    for var, values in df.to_dict().items():
        dataset[var] = list(values.values())
    return dataset


def create_description(series, n_options=100):
    """Create an input description for a series for use in dropdowns

    Parameters
    ----------
    series : pd.Series
        Pandas Series to be described
    n_options : int, optional
        Number of options for dropdown menus, by default 100

    Returns
    -------
    dict
        Description of the series
    """
    col_type = series.dtype

    if is_categorical_dtype(col_type):
        options = list(series.cat.categories)[:n_options]
        field_type = "category"

    elif is_object_dtype(col_type):
        value_counts = series.value_counts(dropna=True)
        options = value_counts.keys().to_list()[:n_options]
        field_type = "category"

    elif is_bool_dtype(col_type):
        options = [True, False]
        field_type = "bool"

    elif is_integer_dtype(col_type):
        options = None
        field_type = "integer"

    elif is_float_dtype(col_type):
        options = None
        field_type = "float"

    else:
        options = None
        field_type = str(col_type)

    input_description = {
        "name": series.name,
        "field_type": field_type,
        "options": options,
    }

    return input_description
