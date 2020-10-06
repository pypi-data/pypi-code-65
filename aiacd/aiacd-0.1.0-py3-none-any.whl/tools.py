def csv_list(file_path):
    import os
    import re

    root_dir = file_path
    files = None
    for dir_, _, files in os.walk(root_dir):
        files = [
            os.path.relpath(os.path.join(root_dir, dirpath, file), root_dir)
            for (dirpath, dirnames, filenames) in os.walk(root_dir)
            for file in filenames
            if re.match("^.*.csv$", file, flags=re.IGNORECASE)
        ]

    return files


def make_directory_and_copy_files(
    o_file, o_path, n_directory, n_subdirectory=None, n_sub_subdirectory=None
):
    """
    :param o_file:  (old) file to be copied
    :param o_path:  (old) path of that file
    :param n_directory: (new) directory to copy old file
    :param n_subdirectory: (new) subdriectory ...
    :param n_sub_subdirectory:  ...
    :return:
    """

    import os
    from shutil import copy
    from shutil import SameFileError

    if n_subdirectory:
        m_directory = os.path.join(n_directory, n_subdirectory)
    else:
        m_directory = n_directory
    try:
        os.makedirs(n_directory)
    except FileExistsError:
        pass
    if not os.path.exists(m_directory):
        os.makedirs(m_directory)
    if n_sub_subdirectory:
        technique_directory = os.path.join(m_directory, n_sub_subdirectory)
        if not os.path.exists(technique_directory):
            os.makedirs(technique_directory)
        try:
            copy(os.path.join(o_path, o_file), technique_directory)
        except SameFileError:
            pass
    else:
        try:
            copy(os.path.join(o_path, o_file), m_directory)
        except SameFileError:
            pass


def csv_list_import(files, profile=3.14, fields=False):
    """

    :param files: List of CSV files
    :param profile: Determines if data is MS/IR/Or TIC (Full MS profile) data
    :type fields: Columns to utilize in dataframe
    """
    import pandas as pd
    import numpy as np

    m_fields = fields
    m_profile = profile_switch(profile)
    df = None
    if m_profile == 1:
        df = [
            pd.read_csv(f, sep=",", header=1, engine="c", usecols=m_fields)
            for f in files
        ]  # Assumes first line is header data
        m_meta_data = pd.concat(
            ([pd.read_csv(f, sep=",", header=0, nrows=0) for f in files]), sort=False
        )
        m_mass = [
            x.split("(", 1)[1].split(")")[0].rstrip("0").rstrip(".")
            for x in m_meta_data
        ]
        m_compound = [
            x.split("Scan", 1)[1].split("2019")[0].rstrip("_") for x in m_meta_data
        ]
        m_compound_mass = [x + y for x, y in zip(m_mass, m_compound)]
        for dataframe, meta in zip(df, m_compound_mass):
            dataframe["Exp"] = meta
    if m_profile == 2:
        # TODO: Implement IR method
        pass
    if m_profile == 3:
        mass = np.arange(18, 400, 1)
        name = ["'{0}{1}'".format("Abudance of ", x) for x in mass]
        res = ["Garbage'{}'".format(x) for x in np.arange(15)]
        for i, j in zip(name, mass):
            res.append(j)
            res.append(i)
        df = [
            pd.read_csv(
                f, sep=",", header=None, engine="c", error_bad_lines=False, names=res
            )
            for f in files
        ]  # Assumes first line is header data  # for dataframe, file in zip(df, files):  #   dataframe['Exp'] = file
    if m_profile == 3.14:
        df = [
            pd.read_csv(f, sep=",", header=None, engine="c", error_bad_lines=False)
            for f in files
        ]
    return df


def profile_switch(profile):
    return {"MS": 1, "IR": 2, "TIC": 3}.get(profile, 3.14)


def mz_matrix(df):
    """

    :type df: Pandas dataframe
    """

    import numpy as np
    import pandas as pd

    for frame in df:
        m_mass = np.arange(18, 400, 1)  # TODO: Param

        m_trashlist = ["Garbage'{}'".format(x) for x in np.arange(15)]
        m_droplist = [c for c in m_trashlist if c in frame.columns]
        frame.drop(m_droplist, axis=1, inplace=True)

        m_dropindex = np.arange(27)
        indexes_to_keep = set(range(frame.shape[0])) - set(m_dropindex)
        frame = frame.take(list(indexes_to_keep))

        frame.fillna(0, inplace=True)

        frame = frame.apply(pd.to_numeric, errors="coerce")
        frame[m_mass] = frame[m_mass].round(0)

        matrix = pd.DataFrame(
            np.zeros(shape=(frame.shape[0], len(m_mass))), columns=m_mass
        )

        row_count = 0
        for row in frame.itertuples(index=False):
            for ix, val in enumerate(row[0:-1:2]):
                if val in m_mass:
                    matrix.at[row_count, int(val)] = row[ix * 2 + 1]
            row_count += 1
        matrix.to_hdf("{}.h5".format("Small2"), key="matrix", mode="w")
        matrix.to_csv("Small2.csv", index=False)


def rename_prefix(file_path, old, new):
    import glob
    import os

    files = glob.glob(file_path + "\\*")
    old_prefix = old
    new_prefix = new
    for f in files:
        os.rename(f, f.replace(old_prefix, new_prefix))


def string_reshaper(substrings, order):
    corrected_file_name = []
    for st in order:
        corrected_file_name.append(substrings[st])
    converted_corrected_file_name = "_".join(corrected_file_name + substrings[3:])
    return converted_corrected_file_name


# Works
def walk(top, maxdepth=None):
    import os

    local_top = os.path.join(os.getcwd(), top)
    dirs = [d.name for d in os.scandir(local_top) if d.is_dir()]
    nondirs = [d.name for d in os.scandir(local_top) if not d.is_dir()]

    yield local_top, dirs, nondirs
    if maxdepth > 1 or None:
        for name in dirs:
            yield from walk(os.path.join(local_top, name), maxdepth - 1)


def flatten_data_sets(data):
    if data:
        if isinstance(data, list):
            return [flat for nest in data for flat in nest]
        else:
            return data
    else:
        return None


def exception(logger):
    import functools

    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                log(
                    logger,
                    "Error: {} Args {} Kwargs {} Function {}".format(
                        e, args, kwargs, function.__name__
                    ),
                )
                raise e

        return wrapper

    return decorator


def log(logger, data_to_log="Error: "):
    import inspect

    func = inspect.currentframe().f_back.f_code
    if isinstance(data_to_log, str):
        data = "{0} <> {1}".format(
            data_to_log, "{}{}".format("Function: ", func.co_name)
        )
    else:
        data = "{0} <> {1}".format(
            ":::".join(data_to_log), "{}{}".format("Function: ", func.co_name)
        )
    logger.debug(data)


def log_factory(lvl="debug", file_out=None, directory=None, message_only=False):
    """

    :rtype: tuple(Debug logger, Warning logger
    """

    import logging
    import os

    if file_out is None:
        file_out = lvl
    if directory is None:
        directory = os.getcwd()
    logger = logging.getLogger("{}".format(file_out))
    warning_log = os.path.join(directory + "\\{}.log".format(file_out))
    if message_only:
        formatter = logging.Formatter("%(message)s")
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    handler = logging.FileHandler(warning_log)
    if lvl == "debug":
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
    if lvl == "warning":
        logger.setLevel(logging.WARNING)
        handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def rename_lims(path, pat=r"(\w.+)(?=19\d{5})(19\d{5})"):
    import os
    from . import re_tools

    local = path
    for r, d, file in os.walk(local):
        for f in file:
            lims = re_tools.re_extract_try(f, pat, 2)
            if lims:
                temp_lims = lims[:-2]
                print(temp_lims)
                temp_lims = temp_lims.replace(temp_lims[-1], "3")
                print(temp_lims)
                temp_lims = temp_lims + lims[-2:]
                print(temp_lims)
                new = str(f).replace(lims, temp_lims)
                old_file = os.path.join(local, str(f))
                new_file = os.path.join(local, new)
                print(new, lims, temp_lims)
                os.rename(old_file, new_file)


def counterfeit_detector():
    path = "C:\\Users\\mjaquier\\Desktop\\NoHolder\\Ref"
    import pandas as pd
    import os

    csv = csv_list(path)
    df = [pd.read_csv(os.path.join(path, file), header=1) for file in csv]
    outlier(df)
    outlier_removed_frame = outlier(df)
    outlier_removed_frame.to_csv(
        os.path.join(path, "outliers_removed.csv"), index=False, header=True
    )
    outlier_removed_frame_summed = outlier_removed_frame.sum(axis=1).div(
        outlier_removed_frame.shape[1]
    )
    outlier_removed_frame_summed_normed = (
        outlier_removed_frame_summed - outlier_removed_frame_summed.mean()
    ) / (outlier_removed_frame_summed.max() - outlier_removed_frame_summed.min())
    outlier_removed_frame_summed_normed = outlier_removed_frame_summed_normed + abs(
        outlier_removed_frame_summed_normed.min()
    )
    wavelengths = df[0].get("cm-1")
    combined_frame = pd.concat(
        [wavelengths, outlier_removed_frame_summed_normed], axis=1
    )
    combined_frame.to_csv(
        os.path.join(
            path, "outliers_removed_average_normed_{}.csv".format(path.split("\\")[-1])
        ),
        index=False,
        header=True,
    )


def outlier(dfs, threshold=3.5):
    import pandas as pd
    import numpy as np

    df_con = pd.concat(dfs, axis=1)
    df_t = df_con.get("%T")
    if df_t is None:
        df_t = df_con.get("A")
    df_t_median = df_t.median(axis=1)
    data = []
    # No data about <which> frame the data comes from is preserved here shouldn't matter.
    for n, n_median in zip(df_t.iterrows(), df_t_median.iteritems()):
        data.append(np.sqrt((n[1] - n_median[1]) ** 2))
    diff = pd.concat(data, axis=1).mean(axis=1)
    med_abs_deviation = np.median(diff)
    modified_z_score = 0.6745 * diff / med_abs_deviation
    # False if outlier
    mask = [x < threshold for x in modified_z_score]
    column_numbers = [x for x in range(df_t.shape[1])]
    drop_table = [col for col, logical in zip(column_numbers, mask) if logical]
    outlier_removed_frame = df_t.iloc[:, drop_table]
    return outlier_removed_frame


def is_dir(lazy_path):
    import glob
    import os

    path_list = [
        globed
        for globed in glob.glob(r"{}".format(lazy_path + "/*"))
        if os.path.isdir(globed)
    ]
    return path_list


def lazy_free_text(path):
    from .re_tools import re_search_strings
    from .re_tools import re_extract_try
    import os
    import glob

    m_search_strings = re_search_strings()
    path_list = glob.glob(path + "\\*")

    for path in path_list:
        for (
            current_path,
            dir_in_cur_path,
            files_in_cur_path,
        ) in os.walk(path):
            for file in files_in_cur_path:
                m_free_text = re_extract_try(
                    file, m_search_strings["search_string_free_text"], 0
                ).split(" ")
                file_to_copy = os.path.join(path, file)
                make_directory_and_copy_files(file_to_copy, path, m_free_text[0])


def get_project_names(path, write=False):
    import glob
    import os

    rls = glob.glob(path + "\\*")
    rls_set = set()
    if write:
        for s_rls in rls:
            s_rls = s_rls.split("\\")[-1]
            rls_set.add(s_rls + "\n")
        cwd = os.getcwd()
        with open(cwd + "\\acd.txt", "w") as file:
            file.writelines(rls_set)
    else:
        for s_rls in rls:
            s_rls = s_rls.split("\\")[-1]
            rls_set.add(s_rls)
        return rls_set
