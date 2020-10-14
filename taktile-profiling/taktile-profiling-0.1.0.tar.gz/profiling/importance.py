import json
import logging
import os

import altair as alt
import numpy as np
import pandas as pd

from profiling.metrics import getloss


def create_importance(endpoint, basepath="results"):
    """Create variable importance graphs"""
    func = endpoint.func
    X = endpoint.X
    y = endpoint.y

    logging.info("Explanations - Calculating variable importance")
    if endpoint.kind == "regression":
        chart, varlist = varimp(func, X, y, metric="Rmse")
    elif endpoint.kind == "binary":
        chart, varlist = varimp(func, X, y, metric="AUC")
    else:
        raise NotImplementedError("Unknown endpoint kind:" + endpoint.kind)

    # Save to disk
    folder = os.path.join(basepath, func.__name__, "anatomy")
    if not os.path.exists(folder):
        os.makedirs(folder)

    fname = "varimp.json"
    fpath = os.path.join(folder, fname)
    chart.save(fpath, format="json")

    fname = "varlist.json"
    fpath = os.path.join(folder, fname)
    with open(fpath, "w") as f:
        json.dump(varlist, f)


def varimp(func, X, y, metric="Rmse", n_max=10000):

    # Sample from large dataframes
    if len(X) > n_max:
        sample = np.random.choice(len(X), n_max, replace=False)
        X = X.iloc[sample]
        y = y.iloc[sample]

    # Baseline performance
    loss = getloss(metric)
    pred = func(X)
    y = np.array(y)
    pred = np.array(pred)
    loss_baseline = loss.metric(pred, y)

    # Performance with permuted columns
    results = {}
    for col in X.columns:
        X_jumbled = X.copy()
        col_jumbled = X_jumbled[col].sample(frac=1, replace=True).values
        X_jumbled[col] = col_jumbled
        pred_jumbled = func(X_jumbled)
        loss_jumbled = loss.metric(pred_jumbled, y)
        results[col] = loss_jumbled

    # Plot
    data = {"Variable": list(results.keys()), "Loss": list(results.values())}

    if loss.greater_is_better:
        df = (
            pd.DataFrame.from_dict(data)
            .sort_values("Loss", ascending=True)
            .astype({"Variable": pd.CategoricalDtype()})
            .assign(delta=lambda x: (-1) * (x["Loss"] - loss_baseline) / loss_baseline)
            .rename(columns={"delta": "Relative Importance"})
        )
    else:
        df = (
            pd.DataFrame.from_dict(data)
            .sort_values("Loss", ascending=False)
            .astype({"Variable": pd.CategoricalDtype()})
            .assign(delta=lambda x: (x["Loss"] - loss_baseline) / loss_baseline)
            .rename(columns={"delta": "Relative Importance"})
        )

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x="Relative Importance",
            y=alt.Y("Variable", sort=None),
            tooltip=[
                alt.Tooltip("Variable"),
                alt.Tooltip("Relative Importance:Q", format=".2f"),
            ],
        )
    )

    # List of variables by importance
    varlist = df["Variable"].tolist()

    return chart, varlist
