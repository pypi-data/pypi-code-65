import warnings
from typing import Iterator, Union

import pandas
from pandas.core.dtypes.common import is_numeric_dtype

from tktl.core.exceptions import exceptions
from tktl.core.loggers import CliLogger

logger = CliLogger()


def validate_func(func, inputs) -> Union[bool, Iterator]:
    pred = func(inputs)

    if not is_numeric_dtype(pred):
        return False
    return pred


def validate_binary(func, inputs):
    pred = validate_func(func, inputs)
    if pred is False:
        return False

    if not 0 <= min(pred):
        raise exceptions.ValidationException(
            "Function output cannot be negative for endpoint kind binary"
        )

    if not max(pred) <= 1:
        raise exceptions.ValidationException(
            "Function output cannot exceed 1 for endpoint kind binary"
        )


def validate_shapes(func, inputs, outputs):
    df = pandas.DataFrame(inputs)
    y = pandas.Series(outputs)
    pred = func(inputs)

    if not len(df) == len(pred):
        return False
    if not len(df) == len(y):
        return False
    return True


def data_frame_convertible(inputs):
    if len(inputs) > 1e6:
        warnings.warn(
            f"inputs is very large (N={len(inputs)}). Please consider using a smaller reference dataset."
        )
    if isinstance(inputs, pandas.DataFrame):
        return True
    try:
        pandas.DataFrame(inputs)
    except ValueError:
        warnings.warn("Could not convert inputs to pd.DataFrame")
        return False
    return True


def series_convertible(y, type_cast=None):
    if isinstance(y, pandas.Series):
        return True
    try:
        y = pandas.Series(y)
        if type_cast:
            y = y.astype(type_cast)
        y.name = y.name or "Outcome"

    except ValueError:
        warnings.warn("Could not convert y to pandas series")
        return False
    return True
