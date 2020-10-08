#!/usr/bin/env python3
from functools import wraps
import logging
from numba import njit, prange
import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
import time

logger = logging.getLogger(__name__)


# Routines related to the "iterative" outlier removal method
@njit(cache=True)
def _trim_np_array(array, perc, min_size=3):
    """Removes extreme valus from both sides of an array

    Takes an array and removes the "50*perc %" largest and
    "50*perc %" smallest elements, provided that the resulting
    trimmed array has a length no smaller tyan min_size
    """
    len_array = len(array)
    n_rm_each_side = int(abs(perc) * 0.5 * len_array)
    truncated_size = len_array - 2 * n_rm_each_side
    if (truncated_size != len_array) and (truncated_size >= min_size):
        array.sort()
        array = array[n_rm_each_side:-n_rm_each_side]
    return array


@njit(cache=True, parallel=True)
def _truncated_means_and_stds(df, perc, min_size=3):
    """
    Truncated means and stdevs for all columns in the dataframe df

    Takes a numpy version "df" of a pandas dataframe (obtained by
    calling the ".to_numpy" method on the original dataframe) and
    returns the truncated mean values and standard deviations for
    all columns. See the _trim_np_array routine for a description
    of the perc and min_size args.
    """
    ncols = df.shape[1]
    means = np.zeros(ncols)
    stds = np.zeros(ncols)
    for icol in prange(ncols):
        array = _trim_np_array(df[:, icol], perc, min_size)
        means[icol] = np.mean(array)
        stds[icol] = np.std(array)
    return means, stds


@njit(cache=True, parallel=True)
def _filter_outliers_iterative_one_iter(
    df, max_n_stdev_around_mean, truncate, weights
):
    """
    A single iteration of the _filter_outliers_iterative function below
    """
    unique_labels = np.unique(df[:, -1])
    for label in unique_labels[unique_labels > -1]:
        indices_for_label = np.transpose(np.argwhere(df[:, -1] == label))[0]

        cols_taken_into_acc = []
        for icol in range(df.shape[1] - 1):
            if icol in [0, 1]:
                if weights[0] < 1e-3:
                    continue
            elif weights[icol - 1] < 1e-3:
                continue
            cols_taken_into_acc.append(icol)
        cols_taken_into_acc = np.array(cols_taken_into_acc)

        df_subset = df[indices_for_label, :][:, cols_taken_into_acc]
        means, stds = _truncated_means_and_stds(df_subset, truncate)
        tol = max_n_stdev_around_mean * stds[:]
        for irow in indices_for_label:
            for icol in cols_taken_into_acc:
                if np.abs(df[irow, icol] - means[icol]) > tol[icol]:
                    # Use "-2" as a "removed by refining methods" flag
                    df[irow, -1] = -2
                    break

    return df


def _filter_outliers_iterative(
    df,
    max_num_iter=100,
    max_n_stdev_around_mean=2.0,
    trunc_perc=0.0,
    weights=None,
    verbose=False,
):
    """
    Detects and assign new labels to obs where abs(obs[i]-obs_mean)>tolerance

    Helper function for the filter_outliers_iterative routine
    """

    used_cols = [
        "lat",
        "lon",
        "alt",
        "mslp",
        "pressure",
        "temperature",
        "humidity",
        "sum_rain_1",
        "cluster_label",
    ]
    df = df.loc[:, df.columns.intersection(used_cols)].to_numpy()
    if weights is None:
        # (lat, lon) -> geodist weight; remove "cluster_label" from weights
        weights = np.ones(len(data_cols) - 2)
    # Set any negative weight value to zero
    weights = np.where(weights < 0, 0.0, weights)

    n_removed_tot = 0
    for i in range(max_num_iter):
        if verbose:
            print("    > Refining scan, iteration ", i + 1, ": ", end=" ")
            start_time = time.time()
        # We use "-2" as a "removed by refining methods" flag
        n_removed_old = np.count_nonzero(df[:, -1] == -2)
        df = _filter_outliers_iterative_one_iter(
            df, max_n_stdev_around_mean, truncate=trunc_perc, weights=weights,
        )
        n_removed_new = np.count_nonzero(df[:, -1] == -2)
        n_removed_this_iter = n_removed_new - n_removed_old
        n_removed_tot = n_removed_tot + n_removed_this_iter
        if verbose:
            print("* rm ", n_removed_this_iter, end=" ")
            print(" stations, ", n_removed_tot, " so far. ", end=" ")
            print("Took ", time.time() - start_time, "s")
        if n_removed_this_iter == 0:
            break
    return df[:, -1]


def filter_outliers_iterative(
    df,
    skip,
    weights,
    trunc_perc=0.25,
    max_num_refine_iter=1000,
    max_n_stdev_around_mean=2,
    **kwargs
):
    df["cluster_label"] = _filter_outliers_iterative(
        df.drop(skip, axis=1),
        max_num_iter=max_num_refine_iter,
        max_n_stdev_around_mean=max_n_stdev_around_mean,
        trunc_perc=trunc_perc,
        weights=weights,
        verbose=logger.getEffectiveLevel() == logging.DEBUG,
    ).astype(int)
    return df


# GLOSH outlier removal method
def filter_outliers_glosh(df, db, **kwargs):
    df["GLOSH"] = db.outlier_scores_
    threshold = min(0.25, df[df["cluster_label"] > -1]["GLOSH"].quantile(0.75))
    outliers_index = (df["cluster_label"] > -1) & (df["GLOSH"] > threshold)
    # Use "-2" as a "removed by refining methods" flag
    df.at[outliers_index, "cluster_label"] = -2
    return df


# Routines related to the LOF outlier removal method
def get_local_outlier_factors(df, distance_matrix, calc_per_cluster=False):
    # See <https://scikit-learn.org/stable/modules/generated/
    # sklearn.neighbors.LocalOutlierFactor.html#>
    unique_labels = df["cluster_label"].unique()
    all_lof_values = np.empty(len(df.index))
    all_lof_values[:] = np.nan
    # Is it better to do this in a per-cluster bases or
    # with the dataset as a whole? Maybe, with such a small
    # n_neighbors, the results won't change much.
    if calc_per_cluster:
        for label in unique_labels:
            if label < 0:
                continue
            indices_mask = df["cluster_label"] == label
            clf = LocalOutlierFactor(
                n_neighbors=min(3, len(indices)), metric="precomputed"
            )
            clf.fit_predict(distance_matrix.subspace(indices))
            all_lof_values[indices] = clf.negative_outlier_factor_
    else:
        indices_mask = df["cluster_label"] > -1
        indices = df.index[indices_mask]
        clf = LocalOutlierFactor(n_neighbors=3, metric="precomputed")
        clf.fit_predict(distance_matrix.subspace(indices))
        all_lof_values[indices] = clf.negative_outlier_factor_
    return all_lof_values


def filter_outliers_lof(df, distance_matrix, **kwargs):
    df["LOF"] = get_local_outlier_factors(df, distance_matrix)
    outliers_index = (df["cluster_label"] > -1) & (df["LOF"] < -1.5)
    # Use "-2" as a "removed by refining methods" flag
    df.at[outliers_index, "cluster_label"] = -2
    return df


# "reclustering" outlier removal method
def suspendlogging(func):
    """
    Adapted from: <https://stackoverflow.com/questions/7341064/
                   disable-logging-per-method-function>
    """

    @wraps(func)
    def inner(*args, **kwargs):
        previousloglevel = logger.getEffectiveLevel()
        try:
            logger.setLevel(logging.WARN)
            return func(*args, **kwargs)
        finally:
            logger.setLevel(previousloglevel)

    return inner


@suspendlogging
def filter_outliers_reclustering(df, distance_matrix, **kwargs):
    n_iter = 0
    n_removed = 0
    n_noise = np.count_nonzero(df["cluster_label"] < 0)
    while n_noise != 0:
        noise_mask = df["cluster_label"] < 0
        df_noise = df[noise_mask]
        i_valid_obs = np.nonzero((~noise_mask).values)[0]

        df = df.drop(df[noise_mask].index)
        df = df.drop(["cluster_label"], axis=1)
        df_rec = run_clustering_on_df(
            df,
            outlier_rm_method=None,
            distance_matrix=distance_matrix.subspace(i_valid_obs),
            calc_silhouette_samples="silhouette_score" in df.columns,
            **kwargs,
        )
        n_noise = np.count_nonzero(df_rec["cluster_label"] < 0)
        df = pd.concat([df_noise, df_rec]).sort_index()
        n_iter += 1
        n_removed += n_noise
        logger.debug("        * Iter #%d: %d new noise pts", n_iter, n_noise)
    logger.debug("    > Done with reclustering. %d removed obs.", n_removed)
    return df


# Higher-level outlier removal routine calling the specific ones defined above
def filter_outliers(df, db, outlier_rm_method, distance_matrix, **kwargs):
    tstart = time.time()
    logger.debug(
        '    > Running outlier removal method "%s" with kwargs=%s',
        outlier_rm_method,
        kwargs,
    )
    # Copy original cluster labels to a new column, so we can keep track
    # of where the removed obs came from
    df["original_cluster_label"] = df["cluster_label"]
    if outlier_rm_method == "glosh":
        rtn = filter_outliers_glosh(df, db=db)
    elif outlier_rm_method == "lof":
        rtn = filter_outliers_lof(df, distance_matrix=distance_matrix)
    elif outlier_rm_method == "reclustering":
        rtn = filter_outliers_reclustering(df, distance_matrix, **kwargs)
    else:
        rtn = filter_outliers_iterative(df, **kwargs)
    logger.debug(
        "      * Done with outlier removal. Elapsed: %.1fs",
        time.time() - tstart,
    )

    return rtn
