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


def create_dependence(endpoint, basepath="results"):
    """Create partial dependence graphs for all variables"""
    func = endpoint.func
    X = endpoint.X
    y = endpoint.y
    folder = os.path.join(basepath, func.__name__, "anatomy", "partialdep")
    if not os.path.exists(folder):
        os.makedirs(folder)

    for var in X.columns:
        logging.info(f"Explanations - Creating partial dependence for {var}")
        fname = var + ".json"
        fpath = os.path.join(folder, fname)
        try:
            chart = partialdep(func, X, y, var)
            chart.save(fpath, format="json")
        except AttributeError:
            logging.warning(f"Could not generate valid chart for {var}")


def partialdep(func, X, y, var):
    """Plot partial dependence"""
    if is_bool_dtype(X[var]) or is_object_dtype(X[var]):
        X[var] = X[var].astype("category")

    if is_categorical_dtype(X[var]):
        return partialdep_cat(func, X, y, var)
    elif is_numeric_dtype(X[var]):
        return partialdep_num(func, X, y, var)
    elif is_datetime64_any_dtype(X[var]):
        return partialdep_num(func, X, y, var)
    else:
        pass


def partialdep_num(func, X, y, var):
    """Plot partial dependence for numerical variables"""
    non_missing = ~X[var].isna()
    X = X[non_missing]
    y = y[non_missing]

    # Downsample large dataframes
    n_obs = len(X)
    n_max = 100
    if n_obs > n_max:
        id_sample = np.random.choice(n_obs, size=n_max, replace=False)
        X = X.iloc[id_sample]
        y = y.iloc[id_sample]

    # Determine evaluation points (deciles)
    if X[var].nunique() >= 10:
        quantiles = np.quantile(
            X[var], q=np.linspace(0.1, 0.9, 9), interpolation="nearest"
        )
    else:
        quantiles = np.sort(X[var].unique())

    # Calculate centered ICE plots
    df_ice = pd.DataFrame()
    for i, quantile in enumerate(quantiles):
        X_mod = X.copy()
        X_mod[var] = quantile
        pred_q = func(X_mod)

        if i == 0:
            offset = pred_q - np.mean(pred_q)  # for centering

        pred_q_centered = pred_q - offset
        df_ice_q = pd.DataFrame(
            {
                "id": np.arange(len(X_mod)),
                var: quantile,
                "Predicted Value": pred_q_centered,
            }
        )
        df_ice = df_ice.append(df_ice_q, ignore_index=True, sort=False)

    # Create plot
    lines = (
        alt.Chart(df_ice)
        .mark_line(strokeOpacity=0.3, color="grey", strokeWidth=2)
        .encode(
            x=var,
            y=alt.Y("Predicted Value:Q", scale=alt.Scale(zero=False)),
            detail="id",
        )
    )
    df_mean = df_ice.groupby(by=var, as_index=False).agg({"Predicted Value": "mean"})
    mean = (
        alt.Chart(df_mean)
        .mark_line(strokeWidth=3, point=True)
        .encode(
            x=var,
            y=alt.Y("Predicted Value:Q", scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip(f"{var}:Q", format=".2f"),
                alt.Tooltip(f"Predicted Value:Q", format=".2f"),
            ],
        )
        .interactive()
    )
    return lines + mean


def partialdep_cat(func, X, y, var, n_max=100, n_sample=50):
    """Plot partial dependence for categorical variables"""

    ordered_categories = list(X[var].cat.categories)[:n_max]
    df_plot = pd.DataFrame()

    for q in ordered_categories:
        X_mod = X.copy()
        X_mod[var] = pd.Categorical(np.repeat(q, len(X)))
        pred_q = func(X_mod)
        rowid = np.arange(len(X_mod))
        df_plot_q = pd.DataFrame({"id": rowid, var: q, "Predicted Value": pred_q})
        df_plot = df_plot.append(df_plot_q, ignore_index=True, sort=False)

    df_plot[var] = df_plot[var].astype("category")

    df_plot_summary = (
        df_plot.groupby(var)
        .agg({"Predicted Value": "mean"})
        .sort_values("Predicted Value", ascending=False)
        .reset_index()
    )

    # Sample
    df_plot_sample = df_plot.query(f"id < {n_sample}")

    # Create plot
    lines = (
        alt.Chart(df_plot_sample)
        .mark_line(strokeOpacity=0.3, color="grey", strokeWidth=2)
        .encode(
            x=alt.X("Predicted Value", scale=alt.Scale(zero=False)),
            y=alt.Y(var, sort=ordered_categories),
            detail="id",
        )
    )
    mean = (
        alt.Chart(df_plot_summary)
        .mark_line(point=True, width=3)
        .encode(
            x="Predicted Value",
            y=alt.Y(var, sort=ordered_categories, scale=alt.Scale(zero=False)),
            tooltip=[var, alt.Tooltip(f"Predicted Value:Q", format=".2f")],
        )
        .interactive()
    )

    return lines + mean
