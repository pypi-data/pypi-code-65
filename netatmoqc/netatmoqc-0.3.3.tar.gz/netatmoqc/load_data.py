#!/usr/bin/env python3
from datetime import datetime
import humanize
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from pytz import timezone
from .dtgs import epoch2datetime, Dtg

logger = logging.getLogger(__name__)


class DataNotFoundError(Exception):
    pass


class DataFrameWithDtgMetadata(pd.DataFrame):
    """ Add DTG metadata to a pandas DataFrame """

    # See <https://pandas.pydata.org/pandas-docs/stable/development/
    #      extending.html#define-original-properties>
    # Define _internal_names and _internal_names_set for temporary properties
    # which WILL NOT be passed to manipulation results.
    # Define _metadata for normal properties which will be passed to
    # manipulation results.

    # temporary properties
    _internal_names = pd.DataFrame._internal_names + ["temp_property"]
    _internal_names_set = set(_internal_names)

    # normal properties
    _metadata = ["_parent_dtg"]

    @property
    def _constructor(self):
        return DataFrameWithDtgMetadata


@np.vectorize
def mslp2sp_coeff(alt):
    """
    Coefficient to convert mean sea-level pressure to pressure at altitude alt
    """
    return 1.0 / (
        int(round(100000 / ((288 - 0.0065 * alt) / 288) ** 5.255)) / 100000
    )


def remove_str_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix) :]
    else:
        return string


@np.vectorize
def shorten_stat_id(stat_id):
    if not isinstance(stat_id, str):
        return stat_id
    # Try first to produce IDs consistent with what Roel does in Netatmo.jl,
    # to be comparable, as there's already people using Netatmo.jl.
    new_id = stat_id[9:17]
    if len(new_id) != 8:
        # Use the strategy originally adapted in netatmoqc if the new ID
        # is shorter than expected
        new_id = remove_str_prefix(stat_id, prefix="enc:16:")
    return new_id[:8]


def read_netatmo_csv(
    path,
    dropna=True,
    fillna=dict(sum_rain_1=0.0),
    recover_pressure_from_mslp=False,
    drop_mslp=None,
    domain=None,
):
    if drop_mslp is None:
        drop_mslp = recover_pressure_from_mslp
    if drop_mslp and not recover_pressure_from_mslp:
        raise ValueError(
            "Cannot have drop_mslp=True and recover_pressure_from_mslp=False"
        )

    data = pd.read_csv(path)
    # Replacing/removing invalid data (NaNs)
    if fillna:
        # fillna may be a key:val map (dict), in which case NaNs in col "key"
        # will be filled with value "val". Fill NaNs before dropping!
        data = data.fillna(fillna)
    if dropna:
        data = data.dropna()

    # Drop the 'enc:16:' stat id prefix and shorten them to 8 chars
    data["id"] = shorten_stat_id(data["id"])

    # The netatmo data I got from Norway has mean sea-level pressure
    # instead of pressure, but the label is "pressure" there. Fix this.
    data = data.rename(columns={"pressure": "mslp"})
    pressure_cols = ["mslp"]
    if recover_pressure_from_mslp:
        data["pressure"] = mslp2sp_coeff(data["alt"]) * data["mslp"]
        pressure_cols += ["pressure"]
    # Make sure columns 'id', 'time_utc', 'lat' and 'lon' appear
    # first AND in this order
    data = data[
        ["id", "time_utc", "lat", "lon", "alt"]
        + pressure_cols
        + ["temperature", "humidity", "sum_rain_1"]
    ]
    if drop_mslp:
        data = data.drop(["mslp"], axis=1)

    data["time_utc"] = epoch2datetime(data["time_utc"])

    if domain is not None:
        # domain is expected to be a ".domains.Domain" obj
        n_before = len(data.index)
        data = domain.trim_obs(data)
        n_after = len(data.index)
        n_rm = n_before - n_after
        if n_rm > 0:
            logger.debug("Removed %d obs outside %s domain", n_rm, domain.name)

    return data.sort_values(by="time_utc").reset_index(drop=True)


def gen_netatmo_fpaths_for_dates(dates, rootdir):
    """
    Return an generator for the paths of the NetAtmo CSV files that need
    to be read in order to get data for date=dt

    NetAtmo CSV files are assumed to have full paths following the pattern
            "rootdir/%Y/%m/%d/%Y%m%dT%H%M%SZ.csv"
    """
    try:
        date_iter = iter(dates)
    except (TypeError):
        date_iter = [dates]
    rootdir = Path(rootdir).resolve()
    for date in sorted(date_iter):
        yyyy = date.strftime("%Y")
        mm = date.strftime("%m")
        dd = date.strftime("%d")
        for f in sorted((rootdir / yyyy / mm / dd).glob("*.csv")):
            yield f


def read_netatmo_data_for_dates(dates, rootdir, **kwargs):
    """
    Return a pd dataframe with data from NetAtmo files for given dates

    kwargs are passed to read_netatmo_csv
    """
    data_from_all_files = {}
    for f in gen_netatmo_fpaths_for_dates(dates, rootdir):
        data_from_all_files[f.stem] = read_netatmo_csv(f, **kwargs)
    if len(data_from_all_files) > 0:
        return pd.concat(data_from_all_files, ignore_index=True)
    else:
        raise DataNotFoundError(
            "Could not find data for date(s)={} under dir '{}'".format(
                dates, rootdir
            )
        )


def datetime_of_netatmo_file(f, fmt="%Y%m%dT%H%M%SZ.csv"):
    dt = datetime.strptime(f.name, fmt)
    return dt.replace(tzinfo=timezone("utc"))


# Reading data for a given DTG instead of date
def gen_netatmo_files_for_time_window(start, end, rootdir):
    """
    List of NetAtmo files corresponding to datetimes within [start, end]

    Returns a list of paths leading to NetAtmo files whose names correspond
    to timestamps lying within the closed interval [start, end].
    """
    start, end = sorted((start, end))
    dates = pd.date_range(start.date(), end.date(), freq="1d")
    for f in gen_netatmo_fpaths_for_dates(dates, rootdir):
        t = datetime_of_netatmo_file(f)
        if t >= start and t <= end:
            yield f


def gen_netatmo_fpaths_for_dtg(dtg, rootdir):
    """
    Paths to NetAtmo files that are likely to contain data for DTG=dtg
    """
    # Add a few minutes to the assimilation window, as
    # netatmo data is gathered every ~10 minutes
    start = dtg.cycle_start - pd.Timedelta("15 minutes")
    end = dtg.cycle_end + pd.Timedelta("15 minutes")
    return gen_netatmo_files_for_time_window(start, end, rootdir=rootdir)


def rm_moving_stations(df):
    # Remove inconsistent stations
    df_grouped_by_id = df.groupby(["id"], as_index=False, sort=False)
    df_temp = df_grouped_by_id[["lat", "lon", "alt"]].agg(["max", "min"])
    inconsistent_stations = df_temp[
        (abs(df_temp["lat"]["max"] - df_temp["lat"]["min"]) >= 1e-4)
        | (abs(df_temp["lon"]["max"] - df_temp["lon"]["min"]) >= 1e-4)
        | (abs(df_temp["alt"]["max"] - df_temp["alt"]["min"]) >= 1e-2)
    ].index.values
    df_ok = df[~df["id"].isin(inconsistent_stations)]
    df_inconsistent = df[df["id"].isin(inconsistent_stations)]
    return df_ok, df_inconsistent


def remove_duplicates_within_cycle(df, dtg):
    """
    Remove duplicates for each station by keeping the one closest to DTG

    If a station reports data multiple times within the time window,
    then keep the one closest to the passed DTG and discard the rest.
    """
    # It seems that using groupby followed by "apply" with a custom
    # function is about 20x slower.
    # Sort using df.loc is better than adding a new col to sort by it. See
    # <stackoverflow.com/questions/39525928/pandas-sort-lambda-function>
    df = df.loc[(abs(df["time_utc"] - dtg)).sort_values().index]
    # We don't need sorting with groupby. HDBSCAN clustering, however,
    # seems to be sensitive to the order in which the rows appear (but
    # not very much so). This seems to be knwon, see, e.g.,
    # <https://github.com/scikit-learn-contrib/hdbscan/issues/265>
    station_groups = df.groupby(["id"], as_index=False, sort=False)
    n_stations_with_duplicates = (station_groups.size()["size"] > 1).sum()
    if n_stations_with_duplicates > 0:
        orig_nobs = len(df.index)
        df = station_groups.first()
        new_nobs = len(df.index)
        logger.debug(
            "Multiple reports from %d stations in DTG=%s. "
            + "Keeping only the one closest to the DTG: "
            + "%s obs now became %s",
            n_stations_with_duplicates,
            dtg,
            orig_nobs,
            new_nobs,
        )
    return df


def read_netatmo_data_for_dtg(
    dtg,
    rootdir,
    return_list_of_removed_stations=False,
    remove_duplicate_stations=True,
    remove_moving_stations=True,
    **kwargs
):
    """
    Return a pd dataframe with data from NetAtmo files for given DTG

    kwargs are passed to read_netatmo_csv
    """
    if not isinstance(dtg, Dtg):
        dtg = Dtg(dtg)

    data_from_all_files = {}
    for f in gen_netatmo_fpaths_for_dtg(dtg, rootdir=rootdir):
        data_from_all_files[f.stem] = read_netatmo_csv(f, **kwargs)
    if len(data_from_all_files) == 0:
        raise DataNotFoundError(
            "Could not find data for DTG={} under dir '{}'".format(
                dtg, rootdir
            )
        )

    df = pd.concat(data_from_all_files, ignore_index=True)
    # Remove DTGs that do not belong to the assimilation time window
    if dtg.assimilation_window.closed_left:
        mask_left = df["time_utc"] >= dtg.assimilation_window.left
    else:
        mask_left = df["time_utc"] > dtg.assimilation_window.left
    if dtg.assimilation_window.closed_right:
        mask_right = df["time_utc"] <= dtg.assimilation_window.right
    else:
        mask_right = df["time_utc"] < dtg.assimilation_window.right
    df = df[mask_left & mask_right]

    if remove_moving_stations:
        # Remove stations that change (lat, lon, alt) within cycle
        df, df_inconsistent_stations = rm_moving_stations(df)
        if len(df_inconsistent_stations.index) > 0:
            logger.debug(
                'Removed %d obs from %d "moving" stations in DTG=%s',
                len(df_inconsistent_stations.index),
                len(df_inconsistent_stations["id"].unique()),
                dtg,
            )
    else:
        logger.warning("Not checking for moving stations")
        df_inconsistent_stations = []

    if remove_duplicate_stations:
        # Remove duplicate data for stations within cycle by keeping
        # the data reported for the timestamp closest to the passed DTG
        df = remove_duplicates_within_cycle(df, dtg)
    else:
        logger.warning("Not removing duplicate stations")

    # Add DTG metadata, to a future reference of how the data was collated
    df = DataFrameWithDtgMetadata(df)
    df._parent_dtg = dtg

    logger.debug(
        "Dataframe has obs from %d stations, with a memsize=%s",
        len(df.index),
        humanize.naturalsize(df.memory_usage(deep=True).sum()),
    )

    if return_list_of_removed_stations:
        return df, df_inconsistent_stations
    else:
        return df
