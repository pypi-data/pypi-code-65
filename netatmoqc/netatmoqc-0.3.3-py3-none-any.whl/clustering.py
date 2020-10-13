#!/usr/bin/env python3
from hdbscan import HDBSCAN, RobustSingleLinkage
import logging
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, OPTICS
from sklearn import metrics
from sklearn.neighbors import LocalOutlierFactor
import time
from .config_parser import UndefinedConfigValue
from .domains import Domain
from .load_data import read_netatmo_data_for_dtg
from .metrics import calc_distance_matrix
from .outlier_removal import filter_outliers

logger = logging.getLogger(__name__)


def sort_df_by_cluster_size(df):
    # Sort df so that clusters with more members are put at the top of the
    # dataframe. The exception if the "-1" label, whichm if present, will
    # always remain at the top. Handy if results are to be plotted.

    # The labels may have been reassigned if the df was passed through
    # an outlier removal routine. Let's keep track of the original ones.
    # This will help keeping obs removed from a cluster by the outlier
    # removed routine close to their origin cluster.
    original_cluster_label_col = "cluster_label"
    if "original_cluster_label" in df.columns:
        original_cluster_label_col = "original_cluster_label"

    # Temporarily add a column with cluster sizes for sorting
    unique_labels, member_counts = np.unique(
        df[original_cluster_label_col], return_counts=True
    )
    label2count_dict = {
        label: count for label, count in zip(unique_labels, member_counts)
    }
    df["parent_cluster_size"] = [
        label2count_dict[label] for label in df[original_cluster_label_col]
    ]
    # Sort dataframe according to frequency, but keep -1 at the top
    df = pd.concat(
        [
            df[df["cluster_label"] == -1],
            df[df["cluster_label"] == -3],
            df[df["cluster_label"] == -4],
            df[~df["cluster_label"].isin([-1, -3, -4])].sort_values(
                [
                    "parent_cluster_size",
                    original_cluster_label_col,
                    "cluster_label",
                ],
                ascending=[False, True, False],
            ),
        ]
    )

    # Reassign labels so that fewer members leads to larger labels.
    # Note that the df unique method does not sort, so this method won't
    # mess up the sorting performed above.
    unique_labels = df[original_cluster_label_col].unique()
    _labels_old2new = dict(
        (old, new)
        for new, old in enumerate(l for l in unique_labels if l >= 0)
    )

    @np.vectorize
    def labels_old2new(old):
        if old < 0:
            return old
        else:
            return _labels_old2new[old]

    for col in ["cluster_label", "original_cluster_label"]:
        try:
            df[col] = labels_old2new(df[col])
        except KeyError:
            pass

    return df.drop("parent_cluster_size", axis=1).reset_index(drop=True)


def weights_dict_to_np_array(
    df, pairwise_diff_weights={}, skip=["id", "time_utc"], default=1
):
    """
    Takes a pandas dataframe and a {column_name:weight} dictionary
    and returns a numpy array of weights to be passed to the routine
    that calculates the distance matrix.

    The "skip" arg lists columns that will not enter the clustering
    and should therefore be skipped.

    If the weight for a non-skipped column of the input dataframe
    are not defined in pairwise_diff_weights, then it will be set to
    default.

    Columns "lat" and "lon" are treated specially, in that they are
    not assigned a weight individually, but rather a single weight
    should be assigned to the "geo_dist" property.
    """

    if df.columns.get_loc("lon") - df.columns.get_loc("lat") != 1:
        raise ValueError("'lat' column is not followed by 'lon' column")

    weights = []
    col2weight = {c: ("geo_dist" if c == "lon" else c) for c in df.columns}
    for col in df.columns[~df.columns.isin(skip + ["lat"])]:
        try:
            weights.append(pairwise_diff_weights[col2weight[col]])
        except (KeyError):
            weights.append(default)
    return np.array(weights, dtype=np.float64)


def get_silhouette_samples(df, distance_matrix):
    # We will only consider true clusters for the calculation of
    # the silhouette coeff, i.e., points with label<0 will be excluded from
    # the calculation. This means that we need to use a slice of the distance
    # matrix in the calculation corresponding to the valid points.
    i_valid_obs = df.reset_index(drop=True).index[df["cluster_label"] >= 0]
    if len(i_valid_obs) == 0:
        logger.warn("No valid obs to calculate silhouette coeffs with")
        return -np.ones(len(df.index))

    reduced_labels = df["cluster_label"].iloc[i_valid_obs]
    if len(reduced_labels.unique()) == 1:
        logger.warn("Only one cluster to calculate silhouette coeffs with")
        return np.ones(len(df.index))

    # Using an intermediate np array is about 10x faster than
    # using df.at[iloc, 'silhouette_score'] = coeff
    all_silhouette_scores = np.empty(len(df.index))
    all_silhouette_scores[:] = np.nan

    reduced_silhouette_scores = metrics.silhouette_samples(
        X=distance_matrix.subspace(i_valid_obs),
        labels=reduced_labels,
        metric="precomputed",
    )
    for iloc, coeff in zip(i_valid_obs, reduced_silhouette_scores):
        all_silhouette_scores[iloc] = coeff

    return all_silhouette_scores


def run_clustering_on_df(
    df,
    method="hdbscan",
    distance_matrix=None,
    distance_matrix_optimize_mode="memory",
    skip=["id", "time_utc"],
    weights_dict={},
    eps=15,  # eps applies only to dbscan
    min_cluster_size=3,  # min_cluster_size applies only to hdbscan
    min_samples=3,
    n_jobs=-1,
    outlier_rm_method=None,
    max_num_refine_iter=50,
    max_n_stdev_around_mean=2.0,
    trunc_perc=0.25,
    calc_silhouette_samples=True,
    **kwargs
):

    method = method.lower()
    # Compute clustering using DBSCAN or HDBSCAN
    if method not in ["dbscan", "hdbscan", "rsl", "optics"]:
        raise NotImplementedError('Method "{}" not available.'.format(method))
    if len(df.index) == 0:
        logger.warning("Dataframe has no rows")
        return df

    # Set weights to be used in the metrics for the various
    # generalised distances. The distances used in the metrics
    # will be used_dist(i) = weight(i)*real_dist(i)
    weights = weights_dict_to_np_array(df, weights_dict)

    # We will not do any df = StandardScaler().fit_transform(df),
    # as we'll use a metric based on earth distances

    if distance_matrix is None:
        # My tests indicate that passing a pre-computed distance matrix to
        # dbscan can be up to 2.5x faster than passing a metrics function (if
        # they both are written in pure python) to fit df. If they are both
        # written in fortran and interfaced via f2py3, or then written in
        # python but jit-compiled with numba, then the relative speed up
        # can reach up to 120x.
        num_threads = -1
        if "num_threads" in kwargs:
            num_threads = kwargs["num_threads"]
        distance_matrix = calc_distance_matrix(
            # Drop columns that won't be used in the clustering
            df.drop(skip, axis=1),
            weights,
            optimize_mode=distance_matrix_optimize_mode,
            num_threads=num_threads,
        )

    # Running clustering with the computed distance matrix
    logger.debug('    > Running clustering method "{}"...'.format(method))
    tstart = time.time()
    if method == "dbscan":
        db = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            metric="precomputed",
            n_jobs=n_jobs,
        ).fit(distance_matrix)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        df["is_core_point"] = core_samples_mask
    elif method == "hdbscan":
        # For more info on the parameters, see
        # <https://hdbscan.readthedocs.io/en/latest/parameter_selection.html>
        db = HDBSCAN(
            min_samples=min_samples,
            min_cluster_size=min_cluster_size,
            metric="precomputed",
            core_dist_n_jobs=n_jobs,
            allow_single_cluster=True,
            # Default cluster_selection_method: 'eom'. Sometimes it leads to
            # clusters that are too big. Using 'leaf' seems better.
            cluster_selection_method="leaf",
            # Merge together clusters that are less than
            # "cluster_selection_epsilon" apart
            # cluster_selection_epsilon=7.5,
        ).fit(distance_matrix)
    elif method == "optics":
        db = OPTICS(
            min_samples=min_samples,
            min_cluster_size=min_cluster_size,
            n_jobs=n_jobs,
            metric="precomputed",
        ).fit(distance_matrix)
    elif method == "rsl":
        db = RobustSingleLinkage(
            # cut: The reachability distance value to cut the cluster
            #      heirarchy at to derive a flat cluster labelling.
            cut=eps,  # default=0.4
            # Reachability distances will be computed with regard to the
            # k nearest neighbors.
            k=min_samples,  # default=5
            # Ignore any clusters in the flat clustering with size less
            # than gamma, and declare points in such clusters as noise points.
            gamma=min_cluster_size,  # default=5
            metric="precomputed",
        ).fit(distance_matrix)
    logger.debug(
        "      * Done with {0}. Elapsed: {1:.1f}s".format(
            method, time.time() - tstart
        )
    )
    # Update df with cluster label info. It is important that this is done
    # right before calling filter_outliers, as the filter_outliers function
    # expects 'cluster_label' to be the last column in the dataframe
    df["cluster_label"] = db.labels_

    # Refine clustering if requested
    # It is important to have 'cluster_label' as the last column
    # when running the iterative refine routine
    if outlier_rm_method:
        df = filter_outliers(
            df,
            db=db,
            outlier_rm_method=outlier_rm_method,
            # Args that apply only to LOF
            distance_matrix=distance_matrix,
            # Args that only apply for the iterative method
            skip=skip,
            max_num_refine_iter=max_num_refine_iter,
            max_n_stdev_around_mean=max_n_stdev_around_mean,
            trunc_perc=trunc_perc,
            weights=weights,
            method=method,
            weights_dict=weights_dict,
            eps=eps,
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            n_jobs=n_jobs,
        )

    # Calculate silhouette scores and update df with this.
    # We'll be reordering the dataframe later, and calculating the score
    # before doing that avoids the need to also reorder the dist matrix.
    if calc_silhouette_samples:
        df["silhouette_score"] = get_silhouette_samples(df, distance_matrix)

    return df


def _cluster_netatmo_obs_one_domain(df, config, **kwargs):
    """Cluster netatmo obs inside a given domain

    Helper for the main routine cluster_netatmo_obs

    kwargs are passed to run_clustering_on_df
    """
    time_start_clustering = time.time()
    logger.debug("Performing clustering...")
    outlier_rm_method = config.get_clustering_opt("outlier_removal.method")
    df = run_clustering_on_df(
        df=df,
        method=config.general.clustering_method,
        distance_matrix_optimize_mode=config.general.custom_metrics_optimize_mode,
        weights_dict=config.get_clustering_opt("obs_weights"),
        eps=config.get_clustering_opt("eps"),
        min_cluster_size=config.get_clustering_opt("min_cluster_size"),
        min_samples=config.get_clustering_opt("min_samples"),
        outlier_rm_method=outlier_rm_method,
        max_num_refine_iter=config.get_clustering_opt(
            "outlier_removal.{}.max_n_iter".format(outlier_rm_method)
        ),
        max_n_stdev_around_mean=config.get_clustering_opt(
            "outlier_removal.{}.max_n_stdev".format(outlier_rm_method)
        ),
        **kwargs,
    )
    time_end_clustering = time.time()
    logger.debug(
        "Done with clustering. Elapsed: {}s".format(
            np.round(time_end_clustering - time_start_clustering, 2)
        )
    )

    return df


def cluster_netatmo_obs(
    config,
    df=None,
    dtg=None,
    return_list_of_removed_stations=False,
    sort_by_cluster_size=False,
    **kwargs
):
    """Main routine for clusterin of netatmo observations

    kwargs are passed to _cluster_netatmo_obs_one_domain.
    """

    if df is None:
        if dtg is None:
            dtg = config.general.dtgs[0]
        logger.debug("Reading data for DTG=%s...", dtg)
        start_read_data = time.time()
        if return_list_of_removed_stations:
            df, rmvd_stations = read_netatmo_data_for_dtg(
                dtg,
                rootdir=config.general.data_rootdir,
                return_list_of_removed_stations=True,
            )
        else:
            df = read_netatmo_data_for_dtg(
                dtg, rootdir=config.general.data_rootdir
            )
        end_read_data = time.time()
        logger.debug(
            "Done reading data for DTG={}. Elapsed: {:.1f}s".format(
                dtg, end_read_data - start_read_data
            )
        )

    # Load domain configs from config
    domain = Domain.construct_from_dict(config.domain)

    # Trim obs to keep only those inside domain. Do this here instead of
    # upon reading so we do this only once.
    n_before = len(df.index)
    df = domain.trim_obs(df)
    n_after = len(df.index)
    n_rm = n_before - n_after
    if n_rm > 0:
        logger.debug("Removed %d obs outside %s domain", n_rm, domain.name)

    df_rejected = None
    if domain.n_subdomains > 1:
        # Perform preliminary clustering on small domains in order to
        # eliminate stations at low cpu/mem cost (O(n^2))
        logger.debug(
            "DTG=%s: Preliminary clustering over %d subdomains...",
            dtg,
            domain.n_subdomains,
        )
        domain_split_dfs = []
        # Silhouette samples are not needed at this point
        pre_clustering_kwargs = kwargs.copy()
        pre_clustering_kwargs["calc_silhouette_samples"] = False
        for isubd, subdomain in enumerate(domain.split()):
            df_sub = subdomain.trim_obs(df)

            min_cluster_size = config.get_clustering_opt("min_cluster_size")
            if min_cluster_size is UndefinedConfigValue:
                min_cluster_size = config.get_clustering_opt("min_samples")
            if len(df_sub.index) < min_cluster_size:
                logger.debug(
                    "DTG=%s: Too few obs (=%d) in subdomain %d/%d. Rejecting.",
                    dtg,
                    len(df_sub.index),
                    isubd + 1,
                    domain.n_subdomains,
                )
                df_sub["cluster_label"] = -1
                domain_split_dfs.append(df_sub)
                continue
            logging.debug(
                "DTG=%s: Pre-clustering %d obs in subdomain %d/%d",
                dtg,
                len(df_sub.index),
                isubd + 1,
                domain.n_subdomains,
            )
            df_sub = _cluster_netatmo_obs_one_domain(
                df=df_sub, config=config, **pre_clustering_kwargs
            )

            domain_split_dfs.append(df_sub)

        # Gather results from preliminary clustering in a single dataframe
        df_cols_prior_to_cluster = df.columns
        df_rejoined_split = pd.concat(domain_split_dfs, ignore_index=True)

        # Mark with flag -3 obs that were removed by outlier removal methods at
        # the pre-clustering stage (which are flagged with "-2")
        df_rejoined_split["cluster_label"].mask(
            df_rejoined_split["cluster_label"] == -2, -3, inplace=True
        )

        # Check for stations missed in the splits, (unlikely, but just in case)
        df_split_missed = df[~df["id"].isin(df_rejoined_split["id"])]
        if len(df_split_missed.index) > 0:
            logger.warning(
                "%d obs missed during subdomain split. Rejecting.",
                len(df_split_missed.index),
            )
            # Mark missed obs with cluster label -4
            df_split_missed["cluster_label"] = -4
            df_rejoined_split = pd.concat(
                [df_rejoined_split, df_split_missed], ignore_index=True
            )

        # Reset df: Only accepted obs will be passed on to the whole-domain
        # clustering. Rejections will be added again to df after that.
        df_rejected = df_rejoined_split[
            df_rejoined_split["cluster_label"] < 0
        ].copy()
        cols_to_drop = [c for c in df_rejected.columns if c not in df.columns]
        df = df_rejoined_split
        df = df[~df["id"].isin(df_rejected["id"])].drop(cols_to_drop, axis=1)

    # Run whole-domain clustering, regardless of splitting in subdomains or not
    if domain.n_subdomains > 1:
        logger.debug("DTG=%s: Main clustering over whole domain...", dtg)
    df = _cluster_netatmo_obs_one_domain(df=df, config=config, **kwargs)

    if df_rejected is not None:
        # Put back eventual obs rejected at the pre-clustering step
        if "original_cluster_label" in df.columns:
            df_rejected["original_cluster_label"] = df_rejected[
                "cluster_label"
            ].copy()
        df = pd.concat([df, df_rejected], ignore_index=True)

    # We only really need this sorting if we're plotting
    if sort_by_cluster_size:
        df = sort_df_by_cluster_size(df)

    # Now we're done.
    if return_list_of_removed_stations:
        return df, rmvd_stations
    else:
        return df


def report_clustering_results(df):
    n_obs = len(df.index)
    noise_data_df = df[df["cluster_label"] < 0]
    n_noise_clusters = len(noise_data_df["cluster_label"].unique())
    noise_count = len(noise_data_df)
    n_clusters = len(df["cluster_label"].unique()) - n_noise_clusters
    n_accepted = n_obs - noise_count
    silhouette_score = df["silhouette_score"].mean(skipna=True)

    logger.info("Number of obs passed to the clustering routine: %d", n_obs)
    logger.info("Estimated number of clusters: %d", n_clusters)
    logger.info("Estimated number of accepted obs: %d", n_accepted)
    logger.info(
        "Estimated number of noise obs: %d (%.1f%% rejection rate)",
        noise_count,
        100.0 * noise_count / n_obs,
    )
    logger.info("Mean silhouette score: {:.3f}".format(silhouette_score))
