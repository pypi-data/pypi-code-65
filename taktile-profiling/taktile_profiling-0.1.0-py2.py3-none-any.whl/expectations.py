import logging
import os

import altair as alt
import numpy as np
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


def create_expectations(endpoint, basepath="results"):
    """Create conditional expectations graphs for all variables"""
    func = endpoint.func
    X = endpoint.X
    y = endpoint.y
    folder = os.path.join(basepath, func.__name__, "anatomy", "condexp")
    if not os.path.exists(folder):
        os.makedirs(folder)

    for var in X.columns:
        logging.info(f"Explanations - Creating conditional expectations for {var}")
        fname = var + ".json"
        fpath = os.path.join(folder, fname)
        try:
            chart = condexp(func, X, y, var)
            chart.save(fpath, format="json")
        except AttributeError:
            logging.warning(f"Could not generate valid chart for {var}")


def condexp(func, X, y, var):
    """Plot conditional expectations"""
    if is_bool_dtype(X[var]) or is_object_dtype(X[var]):
        X[var] = X[var].astype("category")

    if is_categorical_dtype(X[var]):
        return condexp_cat(func, X, y, var)
    elif is_numeric_dtype(X[var]):
        return condexp_num(func, X, y, var)
    elif is_datetime64_any_dtype(X[var]):
        return condexp_datetime(func, X, y, var)
    else:
        pass


def condexp_num(func, X, y, var, n_cut=10):
    """Conditional expectations plot for numerical variables"""
    non_missing = ~X[var].isna()
    X = X[non_missing]
    y = y[non_missing]
    pred = func(X).to_numpy()
    df = X.assign(pred=pred, y=y)
    if df[var].nunique() > n_cut:
        groupvar = df[var] + 1e-6 * np.random.uniform(size=len(df))
        df["groups"] = pd.qcut(groupvar, 10)
    else:
        df["groups"] = df[var]

    df_act = (
        df.groupby("groups")
        .agg({var: "mean", "y": "mean"})
        .assign(Type="Actual Value")
        .rename(columns={"y": y.name})
    )

    df_pred = (
        df.groupby("groups")
        .agg({var: "mean", "pred": "mean"})
        .assign(Type="Predicted Value")
        .rename(columns={"pred": y.name})
    )

    df = df_pred.append(df_act, ignore_index=True)
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(var, scale=alt.Scale(zero=False)),
            y=alt.Y(y.name, scale=alt.Scale(zero=False)),
            color="Type:N",
            tooltip=[
                "Type:N",
                alt.Tooltip(f"{var}:Q", format=".2f"),
                alt.Tooltip(f"{y.name}:Q", format=".2f"),
            ],
        )
        .interactive()
    )

    return chart


def flatten_index(df):
    """Flatten hiearchical column index"""
    df.columns = df.columns.to_flat_index()
    return df


def condexp_cat(func, X, y, var, n_max=25):
    """Conditional expectations plot for categorical variables"""
    pred = func(X).to_numpy()
    df = X.assign(pred=pred, y=y)

    df_agg = (
        df.groupby(var, as_index=False, observed=True)
        .agg({"y": "mean", "pred": ["mean", "count"]})
        .pipe(flatten_index)
        .sort_values(("pred", "count"), ascending=False)
        .head(n_max)  # keep most frequent
        .sort_values(("pred", "mean"), ascending=False)
        .rename(
            columns={
                (var, ""): var,
                ("y", "mean"): "Actual Value",
                ("pred", "mean"): "Predicted Value",
                ("pred", "count"): "N",
            }
        )
    )

    df_agg[var] = df_agg[var].cat.remove_unused_categories()
    ordered_categories = list(df_agg[var].cat.categories)

    df_pred = df_agg.rename(columns={"Predicted Value": y.name}).assign(
        Type="Predicted Value"
    )
    df_act = df_agg.rename(columns={"Actual Value": y.name}).assign(Type="Actual Value")

    chart_pred = (
        alt.Chart(df_pred)
        .mark_circle(opacity=0.9)
        .encode(
            x=alt.X(y.name, scale=alt.Scale(zero=False)),
            y=alt.Y(var, sort=ordered_categories, scale=alt.Scale(zero=False)),
            color="Type:N",
            tooltip=["Type:N", var, alt.Tooltip(f"{y.name}:Q", format=".2f")],
        )
        .interactive()
    )

    chart_act = (
        alt.Chart(df_act)
        .mark_circle(opacity=0.9)
        .encode(
            x=alt.X(y.name, scale=alt.Scale(zero=False)),
            y=alt.Y(var, sort=ordered_categories),
            color="Type:N",
            tooltip=["Type:N", var, alt.Tooltip(f"{y.name}:Q", format=".2f")],
        )
        .interactive()
    )
    chart = chart_pred + chart_act

    return chart


def condexp_datetime(func, X, y, var, n_max=100):
    """Conditional expectations plot for datetime variables"""
    non_missing = ~X[var].isna()
    X = X[non_missing]
    y = y[non_missing]
    pred = func(X).to_numpy()
    df = X.assign(pred=pred, y=y)

    df_agg = (
        df.groupby(var, as_index=False, observed=True)
        .agg({"y": "mean", "pred": ["mean", "count"]})
        .pipe(flatten_index)
        .sort_values(("pred", "count"), ascending=False)
        .head(n_max)  # keep most frequent
        .rename(
            columns={
                (var, ""): var,
                ("y", "mean"): "Actual Value",
                ("pred", "mean"): "Predicted Value",
                ("pred", "count"): "N",
            }
        )
    )

    df_pred = df_agg.rename(columns={"Predicted Value": y.name}).assign(
        Type="Predicted Value"
    )
    df_act = df_agg.rename(columns={"Actual Value": y.name}).assign(Type="Actual Value")

    df = df_pred.append(df_act, ignore_index=True)
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=var,
            y=alt.Y(y.name, scale=alt.Scale(zero=False)),
            color="Type:N",
            tooltip=[
                "Type:N",
                alt.Tooltip(f"{var}:Q", format=".2f"),
                alt.Tooltip(f"{y.name}:Q", format=".2f"),
            ],
        )
        .interactive()
    )

    return chart
