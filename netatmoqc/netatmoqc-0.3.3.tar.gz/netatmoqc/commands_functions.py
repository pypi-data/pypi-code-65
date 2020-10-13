#!/usr/bin/env python3
from datetime import datetime
from functools import partial
import humanize
from joblib import delayed, parallel_backend, Parallel
import logging
import multiprocessing
import numpy as np
import os
import pandas as pd
import platform
import psutil
import subprocess
import time
from .domains import Domain
from .clustering import cluster_netatmo_obs, report_clustering_results
from .config_parser import read_config
from .dtgs import Dtg
from .load_data import (
    rm_moving_stations,
    DataNotFoundError,
)
from .logs import get_logger, logcolor
from .mpi import mpi_parallel
from .plots import (
    DEF_FIGSHOW_CONFIG,
    make_clustering_fig,
    show_cmd_get_fig_from_dataframes,
)
from .save_data import netatmoqc_input2output

logger = logging.getLogger(__name__)


def cluster_obs_single_dtg(args):
    """ Implements the "cluster" command """

    config = read_config(args.config_file)

    try:
        dtg = Dtg(args.dtg)
    except (TypeError):
        dtg = None
    if dtg is None:
        dtg = config.general.dtgs[0]
    logger.info(
        "Running %s on obs for %sDTG=%s%s...",
        config.general.clustering_method,
        logcolor.cyan,
        dtg,
        logcolor.reset,
    )

    if args.savefig:
        # Create outdir at the beginning so users don't
        # waste time in case they can't save results
        outdir = config.general.outdir / "{}_netatmoqc_cluster".format(
            datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        )
        # Allow mkdir to raise eventual exceptions if cannot write to outdir
        outdir.mkdir(parents=True)

    df = cluster_netatmo_obs(
        config=config,
        dtg=args.dtg,
        sort_by_cluster_size=(args.show or args.savefig),
    )
    report_clustering_results(df)

    if args.show or args.savefig:
        logger.info("Preparing figure...")
        domain = Domain.construct_from_dict(config.domain)
        fig = make_clustering_fig(df, domain=domain)
        if args.savefig:
            fpath = str(outdir / "cluster_obs_single_dtg.html")
            logger.info("Saving figure to %s\n", fpath)
            fig.write_html(fpath)
        if args.show:
            fig.show(config=DEF_FIGSHOW_CONFIG)

    logger.info(
        "%sDone with 'cluster' command.%s", logcolor.cyan, logcolor.reset
    )


def _select_stations_single_dtg(dtg, config, args):
    """ This is what "select_stations" does for each DTG """

    logger = get_logger(__name__, args.loglevel)
    logger.info("%sDTG=%s%s: Started", logcolor.cyan, dtg, logcolor.reset)

    # Some control of oversubscription if using mpi.
    # This is not needed when using single-host joblib with "loky"
    cpu_share = -1
    if args.mpi:
        proc_parent = psutil.Process(os.getppid())
        proc_family_size = len(proc_parent.children())
        cpu_share = multiprocessing.cpu_count() // proc_family_size

    tstart = time.time()
    try:
        df, rmvd_stations = cluster_netatmo_obs(
            config=config,
            dtg=dtg,
            return_list_of_removed_stations=True,
            num_threads=cpu_share,
            calc_silhouette_samples=False,
        )
    except DataNotFoundError as e:
        logger.warning(e)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    selected_cols = ["id", "lat", "lon", "alt"]
    rejected_stat_mask = df["cluster_label"] < 0
    df_rejected = df[selected_cols][rejected_stat_mask]
    df_accepted = df[selected_cols][~rejected_stat_mask]
    df_moving = rmvd_stations[selected_cols]

    logger.info("DTG=%s: Done. Elapsed: %.1fs", dtg, time.time() - tstart)
    return df_accepted, df_rejected, df_moving


def select_stations(args):
    """ Implements the "select" command

    This function calls "_select_stations_single_dtg" for each DTG
    (in parallel if requested/possible), and then processes, gathers
    and saves the results.
    """

    tstart_selection = time.time()
    config = read_config(args.config_file)

    # Create outdir at the beginning so users don't
    # waste time in case they can't save results
    outdir = config.general.outdir / "{}_netatmoqc_select".format(
        datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    )
    # Allow mkdir to raise eventual exceptions if cannot write to outdir
    outdir.mkdir(parents=True)

    # Process DTGs in parallel if possible/requested
    if args.mpi:
        logger.info("Parallelising tasks over DTGs using MPI")
        func = partial(_select_stations_single_dtg, config=config, args=args)
        results = mpi_parallel(func, config.general.dtgs)
    else:
        n_procs = int(os.getenv("NETATMOQC_MAX_PYTHON_PROCS", 1))
        if n_procs > 1:
            logger.info("Parallelising tasks over DTGs within a single host")
        # Using the "loky" backend helps avoiding oversubscription
        # of cpus in child processes
        with parallel_backend("loky"):
            results = Parallel(n_jobs=n_procs)(
                delayed(_select_stations_single_dtg)(dtg, config, args)
                for dtg in config.general.dtgs
            )
    logger.info(
        "End of survey over %d DTGs. Combining results..." + "\n",
        len(config.general.dtgs),
    )
    # Gather results: Only accepted and rejected stations for now. Moving
    # stations will be handled after post-processing accepted and rejected
    df_accepted = pd.concat((r[0] for r in results), ignore_index=True)
    df_rejected = pd.concat((r[1] for r in results), ignore_index=True)

    df_accepted, df_moving_accepted = rm_moving_stations(df_accepted)
    if len(df_moving_accepted.index) > 0:
        logger.warning(
            'Removed %d "moving" stations from the list of accepted stations',
            len(df_moving_accepted["id"].unique()),
        )

    df_rejected, df_moving_rejected = rm_moving_stations(df_rejected)
    if len(df_moving_rejected.index) > 0:
        logger.warning(
            'Removed %d "moving" stations from the list of removed stations',
            len(df_moving_rejected["id"].unique()),
        )

    # Let's recover some stations for the list of rejected if they
    # also appear among the df_accepted. Do this based on a
    # tolerance criteria.
    logger.info(
        "Applying station_rejection_tol=%.2f to rescue "
        + 'stations from the "rejected" list',
        config.commands.select.station_rejection_tol,
    )
    accept_counts_per_id = df_accepted["id"].value_counts()
    reject_counts_per_id = df_rejected["id"].value_counts()
    rescued_rejected_stats = []
    # Keep track of rejection rates. We'll use this later.
    id2rejection_rate = dict()
    for stat_id in reject_counts_per_id.index:
        reject_count = reject_counts_per_id[stat_id]
        try:
            accept_count = accept_counts_per_id[stat_id]
        except (KeyError):
            accept_count = 0
        rejection_rate = 1.0 * reject_count / (reject_count + accept_count)
        id2rejection_rate[stat_id] = rejection_rate
        if rejection_rate < config.commands.select.station_rejection_tol:
            rescued_rejected_stats.append(stat_id)
    # Using a rescued_rejected_stats list to modify the dataframes
    # df_accepted/df_rejected is much faster than modifying
    # the dataframes inside the loop above
    rescued_rows = df_rejected.loc[
        df_rejected["id"].isin(rescued_rejected_stats), :
    ]
    df_accepted = df_accepted.append(rescued_rows, ignore_index=True)
    df_rejected = df_rejected.drop(rescued_rows.index)
    if len(rescued_rejected_stats) > 0:
        logger.info(
            "    > Rescuing %d stations rejected in less than %.1f%% of "
            + "occurences",
            len(rescued_rejected_stats),
            100 * config.commands.select.station_rejection_tol,
        )
    else:
        logger.info('    > No stations recovered from "rejected"')

    # We don't need duplicate entries
    df_accepted = df_accepted.drop_duplicates(subset=["id"])
    df_rejected = df_rejected.drop_duplicates(subset=["id"])

    # Now we can handle moving stations
    df_moving = pd.concat(
        [r[2] for r in results] + [df_moving_accepted, df_moving_rejected],
        ignore_index=True,
    )
    df_unique_moving = df_moving["id"].unique()

    df_rejected = df_rejected[~df_rejected["id"].isin(df_unique_moving)]
    df_accepted = df_accepted[
        ~(
            df_accepted["id"].isin(df_unique_moving)
            | df_accepted["id"].isin(df_rejected["id"])
        )
    ]
    if len(df_unique_moving) > 0:
        logger.warning(
            "\n A total of %d unique stations were removed from both\n"
            + " accepted and rejected lists because they changed\n"
            + " at least one of (lat, lon, alt) throughout the survey\n"
            + " These will be saved separately in the moving_stations.csv file",
            len(df_unique_moving),
        )

    ##########################################################################
    # Trim accepted obs to (a possibly coarser version of) the domain's grid #
    ##########################################################################
    # Add (rejection_rate, grid_i, grid_j) columns to df_accepted,           #
    # then, for each (grid_i, grid_j), pick only the station that has the    #
    # lowest rejection_rate                                                  #
    ##########################################################################
    coarse_grid_factor = config.domain.thinning_grid_coarse_factor
    if coarse_grid_factor > 0:
        domain = Domain.construct_from_dict(config.domain)
        thinning_grid_domain = domain.get_thinning_grid_version()
        logger.info(
            "Thinning accepted obs: "
            + "Keeping only 1 station per support grid point"
        )
        logger.info(
            "    > Support grid spacing: %.1f m (%d x the domain's)",
            thinning_grid_domain.gsize,
            coarse_grid_factor,
        )
        n_preliminary_accepted = len(df_accepted.index)

        # (a) Add rejection rate info
        @np.vectorize
        def rej_rate(stat_id):
            try:
                return id2rejection_rate[stat_id]
            except (KeyError):
                return 0.0

        df_accepted["rejection_rate"] = rej_rate(df_accepted["id"])

        # (b) Sort by rejection rate (lower to higher)
        df_accepted = df_accepted.loc[
            df_accepted["rejection_rate"].sort_values(ascending=True).index
        ]

        # (c) Add grid (i, j) info
        icol, jcol = thinning_grid_domain.lonlat2grid(
            df_accepted["lon"].to_numpy(), df_accepted["lat"].to_numpy(),
        )
        df_accepted["i"] = icol
        df_accepted["j"] = jcol

        # (d) rm all but the lowest-rejection-rate station at each grid (i, j)
        grid_trimmed_stations = df_accepted.groupby(
            ["i", "j"], as_index=False, sort=False
        ).first()
        grid_trimmed_stations = grid_trimmed_stations.drop(["i", "j"], axis=1)
        df_accepted = df_accepted.drop(["i", "j"], axis=1)

        # (e) Finally, move to df_rejected those stations that appear in
        #     df_accepted but not in grid_trimmed_stations
        grid_trimmed_mask = df_accepted["id"].isin(grid_trimmed_stations["id"])
        df_rejected = df_rejected.append(df_accepted[~grid_trimmed_mask])
        df_accepted = grid_trimmed_stations

        logger.info(
            "    > Number of stations rejected at the thinning step: %d",
            n_preliminary_accepted - len(df_accepted.index),
        )

    ##################
    # Report results #
    ##################
    total_nstations = sum(
        map(len, [df_accepted.index, df_rejected.index, df_unique_moving,],)
    )
    n_selected = len(df_accepted.index)
    ratio = 100.0 * n_selected / total_nstations

    logger.info(
        "%sFinished with %d accepted stations%s (%.2f%% out of %d)",
        logcolor.cyan,
        n_selected,
        logcolor.reset,
        ratio,
        total_nstations,
    )
    logger.info(
        "That's %d rejections %s(%.2f%% rejection rate)%s",
        total_nstations - n_selected,
        logcolor.cyan,
        100.0 - ratio,
        logcolor.reset,
    )

    ###########################
    # Save and/or show results #
    ###########################
    fpath = outdir / "accepted_stations.csv"
    logger.info(
        "%sSaving accepted station data to%s %s",
        logcolor.cyan,
        logcolor.reset,
        fpath,
    )
    df_accepted.to_csv(fpath, index=None, mode="w")

    fpath = outdir / "rejected_stations.csv"
    logger.info(
        "%sSaving rejected station data to%s %s",
        logcolor.cyan,
        logcolor.reset,
        fpath,
    )
    df_rejected.to_csv(fpath, index=None, mode="w")

    fpath = outdir / "moving_stations.csv"
    logger.info(
        "%sSaving moving station data%s to %s\n",
        logcolor.cyan,
        logcolor.reset,
        fpath,
    )
    df_moving.to_csv(fpath, index=None, mode="w")

    # Save data from selected stations in OBSOUL file format
    netatmoqc_input2output(
        config.general.dtgs,
        netatmo_data_rootdir=config.general.data_rootdir,
        selected_stations=df_accepted["id"],
        outdir=outdir,
        loglevel=args.loglevel,
        use_mpi=args.mpi,
        save_csv=True,
        save_obsoul=args.save_obsoul,
        obsoul_export_params=config.general.obsoul_export_params,
    )

    # We're now done.
    elapsed = time.time() - tstart_selection
    logger.info(
        "%sDone with 'select' command, %d DTGs. Elapsed: %s (~%s per DTG)%s",
        logcolor.cyan,
        len(config.general.dtgs),
        humanize.precisedelta(elapsed),
        humanize.precisedelta(elapsed / len(config.general.dtgs)),
        logcolor.reset,
    )


# Code related to the csv2obsoul command
def csv2obsoul(args):
    """ Implements the "csv2obsoul" command"""

    config = read_config(args.config_file)

    # Create outdir at the beginning so users don't
    # waste time in case they can't save results
    outdir = config.general.outdir / "{}_netatmoqc_csv2obsoul".format(
        datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    )
    # Allow mkdir to raise eventual exceptions if cannot write to outdir
    outdir.mkdir(parents=True)

    netatmoqc_input2output(
        config.general.dtgs,
        netatmo_data_rootdir=config.general.data_rootdir,
        dropna=args.dropna,
        fillna=args.fillna,
        rm_duplicate_stations=args.rm_duplicate_stations,
        rm_moving_stations=args.rm_moving_stations,
        outdir=outdir,
        loglevel=args.loglevel,
        use_mpi=args.mpi,
        save_csv=False,
        save_obsoul=True,
        obsoul_export_params=config.general.obsoul_export_params,
    )

    logger.info(
        "%sDone with 'csv2obsoul' command.%s", logcolor.cyan, logcolor.reset
    )


# Code related to the "show" command
def _open_file_with_default_app(fpath):
    if platform.system() == "Windows":
        os.startfile(fpath)
    elif platform.system() == "Darwin":
        subprocess.call(("open", fpath))
    else:
        subprocess.call(("xdg-open", fpath))


def show(args):
    """ Implements the 'show' command """

    logger = get_logger(__name__, args.loglevel)

    config = read_config(args.config_file)
    domain = Domain.construct_from_dict(config.domain)

    if args.domain:
        fig = domain.get_fig(display_grid_max_gsize=20000.0)
        fig.update_layout(
            legend=dict(
                orientation="h", xanchor="center", x=0.5, yanchor="top", y=0.0,
            )
        )
        fig.show(config=DEF_FIGSHOW_CONFIG)

    if args.config:
        logger.info("TOML config dump:\n\n%s", config.toml_dumps())

    dataframes = {}
    for fpath in args.file_list:
        if fpath.suffix == ".csv":
            logger.info("Reading data from file %s", fpath)
            dataframes[fpath.name] = pd.read_csv(fpath)
        elif fpath.suffix in [".htm", ".html"]:
            logger.info("Openning file '%s'", fpath)
            _open_file_with_default_app(fpath)
        else:
            logger.warning(
                "Only html and csv files supported. Skipping file '%s'", fpath
            )

    if len(dataframes) > 0:
        fig = show_cmd_get_fig_from_dataframes(args, dataframes, domain)
        fig.show(config=DEF_FIGSHOW_CONFIG)
