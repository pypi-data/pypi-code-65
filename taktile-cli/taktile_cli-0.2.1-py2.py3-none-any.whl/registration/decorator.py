import functools
import warnings
from abc import ABC, abstractmethod
from typing import Any, Callable

import pandas
import pandas.api.types as ptypes

from tktl.core.exceptions import exceptions
from tktl.core.loggers import CliLogger
from tktl.registration.validation import (
    data_frame_convertible,
    series_convertible,
    validate_binary,
    validate_func,
    validate_shapes,
)

logger = CliLogger()


class Endpoint(ABC):
    KIND: str

    def __init__(self, func: Callable):
        self.pandas_convertible: bool = True
        self.profiling_supported: bool = True
        self.func = func

    @abstractmethod
    def _validate(self, func, X, y):
        raise NotImplementedError


class TabularEndpoint(Endpoint):
    kind = "tabular"

    def __init__(self, func, X, y, type_cast=None):
        super().__init__(func)
        self.X = X
        self.y = y
        self.pandas_convertible = data_frame_convertible(X) and series_convertible(
            y, type_cast=type_cast
        )
        self.profiling_supported = self._validate(func, X, y)
        self._drop_missing_values()

    def _drop_missing_values(self):
        not_missing = [i for i, v in enumerate(self.y) if not pandas.isna(v)]
        n_missing = len(self.y) - len(not_missing)
        if n_missing > 0 and self.pandas_convertible:
            warnings.warn(f"y contains {n_missing} missing values that will be dropped")
            self.X = self.X.iloc[not_missing]
            self.y = self.y.iloc[not_missing]

    def _validate_func(self, func, X):
        preds = func(X)
        if not ptypes.is_numeric_dtype(pandas.Series(preds)):
            return False
        return True

    def _validate(self, func, X, y):
        if not self.pandas_convertible:
            return False
        return self._validate_func(self.func, self.X) and validate_shapes(
            self.func, self.X, self.y
        )


class BinaryEndpoint(TabularEndpoint):
    kind = "binary"

    def __init__(self, func, X, y):
        super().__init__(func, X, y, type_cast=bool)

    def _validate_func(self, func, X):
        return validate_binary(func=self.func, inputs=self.X)


class RegressionEndpoint(TabularEndpoint):
    kind = "regression"

    def __init__(self, func, X, y):
        super().__init__(func, X, y)

    def _validate_func(self, func, X):
        return False if validate_func(func=self.func, inputs=self.X) is False else True


class AuxiliaryEndpoint(Endpoint):
    kind = "auxiliary"

    def __init__(self, func, payload_model=None, response_model=None):
        super().__init__(func)
        self.func = func
        self.payload_model = payload_model
        self.response_model = response_model
        self.pandas_convertible = False
        self.profiling_supported = False
        self._validate(func)

    def _validate(self, func, **kwargs):
        assert isinstance(self.func, Callable)


class Tktl:
    def __init__(self):
        self.endpoints = []

    # This is the user-facing decorator for function registration
    def endpoint(
        self,
        func: Callable = None,
        kind: str = "regression",
        X: Any = None,
        y: Any = None,
        payload_model=None,
        response_model=None,
    ):
        """Register function as a Taktile endpoint

        Parameters
        ----------
        func : Callable, optional
            Function that describes the desired operation, by default None
        kind : str, optional
            Specification of endpoint type ("regression", "binary", "auxiliary"),
            by default "regression"
        X : pd.DataFrame, optional
            Reference input dataset for testing func. Used when argument "kind"
            is set to "regression" or "binary", by default None.
        y : pd.Series, optional
            Reference output for evaluating func. Used when argument "kind"
            is set to "regression" or "binary", by default None.
        payload_model:
            Type hint used for documenting and validating payload. Used in
            auxiliary endpoints only.
        response_model:
            Type hint used for documenting and validating response. Used in
            auxiliary endpoints only.

        Returns
        -------
        Callable
            Wrapped function
        """
        if func is None:
            return functools.partial(
                self.endpoint,
                kind=kind,
                X=X,
                y=y,
                payload_model=payload_model,
                response_model=response_model,
            )

        if kind == "tabular":
            endpoint = TabularEndpoint(func=func, X=X, y=y)
        elif kind == "regression":
            endpoint = RegressionEndpoint(func=func, X=X, y=y)
        elif kind == "binary":
            endpoint = BinaryEndpoint(func=func, X=X, y=y)
        elif kind == "auxiliary":
            endpoint = AuxiliaryEndpoint(
                func=func, payload_model=payload_model, response_model=response_model
            )
        else:
            raise exceptions.ValidationException(f"Unknown endpoint kind: '{kind}'")

        self.endpoints.append(endpoint)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            pred = func(*args, **kwargs)
            return pred

        return wrapper
