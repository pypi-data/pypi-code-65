from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from profiling.accuracy import create_accuracy
from profiling.dependence import create_dependence
from profiling.expectations import create_expectations
from profiling.importance import create_importance
from tktl import Tktl

# Generate test data
X = pd.DataFrame.from_dict(
    {
        "Integer": [1, 2, 3],
        "Float": [None, 2.0, 3.0],
        "Object": [None, "", "c"],
        "Categorical": ["a", "b", "c"],
        "Date": [date(2020, 1, 1), date(2020, 1, 2), date(2020, 1, 3)],
        "Datetime": [datetime(2020, 1, 1), None, datetime(2020, 1, 3)],
    }
).astype({"Categorical": "category"})
y_regression = pd.Series([5, 3.2, -0.2], name="Outcome")
y_binary = pd.Series([True, False, True], name="Outcome")

# Instantiate client and generate test endpoints
tktl = Tktl()


@tktl.endpoint(kind="regression", X=X, y=y_regression)
def regression(X):
    return np.random.uniform(size=len(X))


@tktl.endpoint(kind="binary", X=X, y=y_binary)
def binary(X):
    return np.random.uniform(size=len(X))


def test_expectations(tmpdir):
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        create_expectations(endpoint, basepath=tmpdir)
        for var in X.columns:
            path = Path(tmpdir, name, "anatomy", "condexp", var + ".json")
            assert path.exists()


def test_dependence(tmpdir):
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        create_dependence(endpoint, basepath=tmpdir)
        for var in X.columns:
            path = Path(tmpdir, name, "anatomy", "partialdep", var + ".json")
            assert path.exists()


def test_importance(tmpdir):
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        create_importance(endpoint, basepath=tmpdir)
        assert Path(tmpdir, name, "anatomy", "varimp.json").exists()


def test_accuracy(tmpdir):
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        create_accuracy(endpoint, basepath=tmpdir)
        assert Path(tmpdir, name, "accuracy", "calibration.json").exists()
        assert Path(tmpdir, name, "accuracy", "metrics.json").exists()
        assert Path(tmpdir, name, "accuracy", "errors.json").exists()
