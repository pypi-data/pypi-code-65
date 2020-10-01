import yaml
import pandas as pd
import time
from pandas.api.types import CategoricalDtype


def read_metadata(filename):
    # read the metadata from the yaml file
    with open(filename, 'r') as stream:
        data_yaml = yaml.load(stream)
    return data_yaml


def check_schema(df, meta_columns):
    # check  the schema based on yaml file
    for col in meta_columns:
        assert col in df.columns, f'"{col}" not in dataframe columns'


def load_df_file(csv_filename, yaml_filename, encoding='utf-8'):
    # loads the dataframe and checks the schema

    # check encoding is of expected options
    assert encoding in ('latin-1', 'utf-8'), 'unknown encoding'

    # get the expected columns
    expected_columns = read_metadata(yaml_filename)['columns']

    # read the dataframe
    df = pd.read_csv(csv_filename, encoding=encoding)

    # check schema
    check_schema(df, expected_columns)

    # drop duplicated rows
    df = df.drop_duplicates()

    # clean the MRN if MRN in columns
    if ('MRN' in list(df.columns)) | ('mrn' in list(df.columns)):
        df = clean_MRN(df)

    return df


def clean_MRN(df):
    # cleans the MRN column by dropping nan or replacing mrn with MRN

    # fix lowercase mrn
    if 'mrn' in list(df.columns):
        df = df.rename(columns={'mrn': 'MRN'})

    # check that MRN is in the columns
    assert 'MRN' in df.columns, 'MRN not in columns'

    # convert to numeric
    df['MRN'] = pd.to_numeric(df['MRN'], errors='coerce')

    # drop nan
    df = df.dropna(subset=['MRN']).copy()
    assert df['MRN'].isnull().sum() == 0, 'missing MRNs'

    # convert to int
    df['MRN'] = df['MRN'].astype('int64')
    return df


def load_df_with_dates(csv_filename, yaml_filename, dates, date_formats, encoding='utf-8'):
    # this function loads the csv and converts the dates

    # load the df
    df = load_df_file(csv_filename, yaml_filename, encoding)

    # check the dates and formats are right length
    assert len(dates) == len(date_formats), 'number of formats does not match number of dates'

    # check_schema is correct
    check_schema(df, dates)

    for date, date_format in zip(dates, date_formats):
        df[date] = pd.to_datetime(df[date], format=date_format, errors='coerce')
        # error if not date format
        assert (type(df[date].iloc[0]) == pd.Timestamp) | pd.isna(df[date].iloc[0]), f'"{date}" not date format'

        # error if all are null (catches wrong format)
        if len(df) > 0:
            assert df[date].notnull().sum() != 0, 'all dates are missing, check date format'
    return df


def keep_first(df, group_cols, my_date):
    # this function groups the dataframe on group_cols and keeps the first my_date

    assert df.duplicated(subset=group_cols + [my_date]).sum() == 0, 'duplicated dates'

    df = (df.sort_values(group_cols + [my_date])).reset_index(drop=True)

    for c in group_cols:
        assert df[c].isnull().sum() == 0, 'null values for groupby in ' + c

        z_grp = (df.groupby(group_cols).nth(0)).reset_index()
    assert z_grp.duplicated(subset=group_cols).sum() == 0, 'duplicated rows'

    return z_grp


def check_merge_keep(df_left, df_right, left_date, right_date, merge_cols, groupby_cols):
    assert left_date in df_left.columns, 'left_date not in left columns'
    assert right_date in df_right.columns, 'right_date not in right columns'

    for m in merge_cols:
        assert m in df_left.columns, f'"{m}" not in left columns'
        assert m in df_right.columns, f'"{m}" not in right columns'

    for g in groupby_cols:
        assert g in df_left.columns, f'"{g}" groupby not in left columns'

    for g in [c for c in groupby_cols if c not in merge_cols]:
        assert g not in df_right.columns, f'"{g}" in right columns'

    assert type(df_left[left_date].iloc[0]) == pd.Timestamp, 'left_date not time stamp'
    assert type(df_right[right_date].iloc[0]) == pd.Timestamp, 'right_date not time stamp'

    assert df_right[merge_cols + [right_date]].duplicated().sum() == 0, 'duplicated dates'


def merge_keep_first(df_left, df_right, left_date, right_date, merge_cols, groupby_cols, use_equal):
    # track the original dtypes
    # orig = df_right.dtypes.to_dict()
    # orig.update(df_left.dtypes.to_dict())

    # check inputs
    check_merge_keep(df_left, df_right, left_date, right_date, merge_cols, groupby_cols)

    # merge df_left and df_right and keep the first right_date after left_date for groupby_cols
    z = pd.merge(df_left, df_right, on=merge_cols, how='left')

    for g in groupby_cols:
        assert g in z.columns, f'"{g}" groupby not in merge columns'

    # only keep the rows where left_date < right_date or <= depending on use_equal
    if use_equal == 1:
        rows = ((z[left_date].dt.normalize()) <= (z[right_date].dt.normalize()))
    else:
        rows = ((z[left_date].dt.normalize()) < (z[right_date].dt.normalize()))
    z = z.loc[rows]

    # keep the row with first right_date
    z_first = keep_first(z, groupby_cols, right_date)
    df = pd.merge(df_left, z_first[list(set(groupby_cols + list(df_right.columns)))], on=groupby_cols, how='left')

    assert len(df) == len(df_left), 'number of samples changed'

    # doublecheck the dtypes
    # df = df.apply(lambda x: x.astype(orig[x.name]))

    return df


def keep_last(df, group_cols, my_date):
    # this function groups the dataframe on group_cols and keeps the last my_date

    assert df.duplicated(subset=group_cols + [my_date]).sum() == 0, 'duplicated dates'

    df = (df.sort_values(group_cols + [my_date], ascending=False)).reset_index(drop=True)

    for c in group_cols:
        assert df[c].isnull().sum() == 0, 'null values for groupby in ' + c

        z_grp = (df.groupby(group_cols).nth(0)).reset_index()
    assert z_grp.duplicated(subset=group_cols).sum() == 0, 'duplicated rows'

    return z_grp


def merge_keep_last(df_left, df_right, left_date, right_date, merge_cols, groupby_cols, use_equal):
    """
    WHAT: This is a implementation of Andy's original code that merged the data to keep the last value when 2 DataFrame is
      merged.
    WHY: Since there was a merge that merged with every possible combination, caused memory issue and was taking long time
         merge 2 DataFrame
    ASSUMES: Matched data generated with this function with data generated by Andy's original code.
    FUTURE IMPROVEMENTS: N/A
    WHO: SKL 2020/07/20
    SAMPLE OUTPUT: N/A

    :param df_left: sample DataFrame with merge col and left_date a columns
    :param df_right: DataFrame to merge df_left
    :param left_date: date column from df_left to merge with df_right.
    :param right_date: date column from df_right to merge with df_left
    :param merge_cols: list of columns to merge the 2 dfs.
    :param groupby_cols: columns to group by DataFrame in Andy's code. Here we use this to sort the DataFrame
    :param use_equal: Flag to either include same day. If use_equal ==1 then we use same day data, else we skip same day
           data
    :return: DataFrame that has last result as a row.
    """
    print('-getting last data', end='...')
    t1 = time.time()
    # check inputs
    check_merge_keep(df_left, df_right, left_date, right_date, merge_cols, groupby_cols)

    # Sorting the df_left by group_cols. Sorting is necessary for merge_asof to work.
    df_left = df_left.sort_values(groupby_cols)
    df_right = df_right.sort_values([right_date])

    # Create a new column to store the original date. This is done to restore the date and time which is lost when date
    # is normalized in later step. ( Normalization is done here so it matches the result from original merge_keep_last
    # function created by Andy.
    df_left["original_left_date"] = df_left[left_date]
    df_right['original_right_date'] = df_right[right_date]

    # Normalization of dates.
    df_left[left_date] = df_left[left_date].dt.normalize()
    df_right[right_date] = df_right[right_date].dt.normalize()

    # Only keep the row where date is not empty
    df_right = df_right.loc[df_right[right_date].notnull()]

    # Merge 2 DataFrame. Here tolerance is set up to be 6 years to capture data from earlier date.
    # If we use more than 6 years worth of data, tolerance needs to be changed.
    # If use_equal == 1, merge occurs in same date data
    # If use_equal !=1, merge occurs on older data and will skip same date data.
    if use_equal == 1:
        df = pd.merge_asof(df_left.sort_values([left_date]), df_right, left_on=left_date,
                           right_on=right_date, by=merge_cols, tolerance=pd.Timedelta('2190days'))
    else:
        df = pd.merge_asof(df_left.sort_values([left_date]), df_right, left_on=left_date,
                           right_on=right_date, by=merge_cols, tolerance=pd.Timedelta('2190days'),
                           allow_exact_matches=False)

    assert len(df) == len(df_left), 'number of samples changed'

    # Dropping normalized dates columns.
    df.drop(columns=[left_date, right_date], inplace=True)

    # Renaming the dates column back to it's original name.
    df.rename(columns={'original_left_date': left_date, "original_right_date": right_date}, inplace=True)

    t2 = time.time()
    print('done in', t2 - t1)
    return df


def keep_last_by_col(df, group_cols, data_cols, my_date):
    # this function groups the dataframe on group_cols and keeps the last numeric value by date for each column column

    assert df.duplicated(subset=group_cols + [my_date]).sum() == 0, 'duplicated dates'
    # sort by date in descending order
    df = (df.sort_values(group_cols + [my_date], ascending=False)).reset_index(drop=True)

    # check groupby cols are not-null
    for c in group_cols:
        assert df[c].isnull().sum() == 0, 'null values for groupby in ' + c

    # get the first non-null value if it exists for each column
    all_df = []
    for c in data_cols:
        all_df.append(df[group_cols + [c]].groupby(group_cols).nth(0, dropna='any'))
    # concat all columns
    df_grp = pd.concat(all_df, axis=1).reset_index()

    assert df_grp.duplicated(subset=group_cols).sum() == 0, 'duplicated rows'

    return df_grp


def merge_keep_last_by_col(df_left, df_right, left_date, right_date, merge_cols, groupby_cols, use_equal, data_cols):
    print('-getting last data', end='...')
    t1 = time.time()

    # track the original dtypes
    orig = df_right.dtypes.to_dict()
    orig.update(df_left.dtypes.to_dict())

    # check inputs
    check_merge_keep(df_left, df_right, left_date, right_date, merge_cols, groupby_cols)

    # merge df_left and df_right and keep the first right_date after left_date for groupby_cols
    z = pd.merge(df_left, df_right, on=merge_cols, how='left')

    for g in groupby_cols:
        assert g in z.columns, f'"{g}" groupby not in merge columns'

    # only keep the rows where left_date < right_date or <= depending on use_equal
    if use_equal == 1:
        rows = ((z[left_date].dt.normalize()) >= (z[right_date].dt.normalize()))
    else:
        rows = ((z[left_date].dt.normalize()) > (z[right_date].dt.normalize()))
    z = z.loc[rows]

    # keep the non-null value with last right_date for each column
    z_last = keep_last_by_col(z, groupby_cols, data_cols, right_date)
    df = pd.merge(df_left, z_last[groupby_cols + data_cols], on=groupby_cols, how='left')

    assert len(df) == len(df_left), 'number of samples changed'

    # doublecheck the dtypes
    df = df.apply(lambda x: x.astype(orig[x.name]))

    t2 = time.time()
    print('done in', t2 - t1)
    return df


def check_calc_window(merge_cols, df_samples, cols_samples, date_samples, \
                      df_data, cols_data, date_data):
    # verifies the inputs of calc_window
    assert date_samples in df_samples.columns, 'date_samples not in df_samples columns'
    assert date_data in df_data.columns, 'date_data not in df_data columns'

    for m in merge_cols:
        assert m in df_samples.columns, f'"{m}" not in df_samples columns'
        assert m in df_data.columns, f'"{m}" not in df_data columns'

    for g in cols_samples:
        assert g in df_samples.columns, f'"{g}" groupby not in df_samples columns'

    for g in [c for c in cols_samples if c not in merge_cols]:
        assert g not in df_data.columns, f'"{g}" in df_data columns'

    assert type(df_samples[date_samples].iloc[0]) == pd.Timestamp, 'date_samples not time stamp in df'
    assert type(df_data[date_data].iloc[0]) == pd.Timestamp, 'date_data not time stamp in df'


def calc_window(merge_cols, df_samples, cols_samples, date_samples, \
                df_data, cols_data, date_data, \
                window_days):
    # verify inputs
    check_calc_window(merge_cols, df_samples, cols_samples, date_samples, \
                      df_data, cols_data, date_data)

    # merge the samples on the data
    df = pd.merge(df_samples[list(set(cols_samples + [date_samples]))], df_data, on=merge_cols, how='left')

    # restrict to samples inside the date window
    df = df.loc[(df[date_data] >= (df[date_samples] - pd.to_timedelta(window_days, unit='d'))) & \
                (df[date_data] < (df[date_samples]))]

    # calculate features
    df_mean = df.groupby(cols_samples)[cols_data].mean().add_suffix('_%d_MEAN' % window_days)
    df_max = df.groupby(cols_samples)[cols_data].max().add_suffix('_%d_MAX' % window_days)
    df_min = df.groupby(cols_samples)[cols_data].min().add_suffix('_%d_MIN' % window_days)
    df_std = df.groupby(cols_samples)[cols_data].std().add_suffix('_%d_STD' % window_days)
    # add slope here
    df2 = pd.concat([df_mean, df_max, df_min, df_std], axis=1).reset_index()

    # merge on cols_samples to pick up nans
    df_window = pd.merge(df_samples[cols_samples], df2, on=cols_samples, how='left')

    return df_window


def preprocess_history(merge_cols, df_samples, cols_samples, date_samples, \
                       df_data, cols_data, date_data, \
                       window_days):
    # this function processes the historical data into buckets based on window_days
    # Mostly just a wrapper around calc_window
    all_dfs = []
    for w in window_days:
        # add windowing data to the samples
        t1 = time.time()
        print('-Historical window %d...' % w, end='')
        df_window = calc_window(merge_cols, df_samples, cols_samples, date_samples, \
                                df_data, cols_data, date_data, \
                                w)
        all_dfs = all_dfs + [df_window.set_index(cols_samples)]
        t2 = time.time()
        print('done in ', t2 - t1)
    return pd.concat(all_dfs, axis=1).reset_index()


def preprocess_last_history(merge_cols, df_samples, cols_samples, date_samples, \
                            df_data, cols_data, date_data, \
                            window_days, by_col):
    # this function gets the last and calculates historical data

    check_merge_keep(df_samples, df_data, date_samples, date_data, merge_cols, cols_samples)
    check_calc_window(merge_cols, df_samples, cols_samples, date_samples, \
                      df_data, cols_data, date_data)

    # get the last value
    use_equal = 1
    # gets the last value by column or by row
    if by_col:
        df_last_samples = merge_keep_last_by_col(df_samples, df_data, date_samples, date_data, merge_cols, cols_samples,
                                                 use_equal, cols_data)
    else:
        df_last_samples = merge_keep_last(df_samples, df_data, date_samples, date_data, merge_cols, cols_samples,
                                          use_equal)

    # calculate the historical lab data
    df_hist = preprocess_history(merge_cols, df_samples, cols_samples, date_samples, \
                                 df_data, cols_data, date_data, \
                                 window_days)

    # set index
    df_last_samples = df_last_samples.set_index(cols_samples)
    df_hist = df_hist.set_index(cols_samples)

    # combine the data based on index
    df_combined = pd.concat([df_last_samples, df_hist], axis=1)
    df_combined = df_combined.reset_index()

    assert len(df_combined) == len(df_samples), 'number of samples increased'

    # add deltas to the data set
    cols_diff = ['MEAN', 'MIN', 'MAX']
    df_combined = add_hist_deltas(df_combined, cols_data, window_days, cols_diff)

    return df_combined


def group_data_date(df_data, date_data, cols_data):
    # groupby mrn and date
    df_data = df_data[cols_data + [date_data, 'MRN']].groupby(['MRN', date_data]).mean()
    df_data = df_data.reset_index()

    # preprocess the data (depends if development or production)
    assert df_data.duplicated(subset=['MRN', date_data]).sum() == 0, 'duplicated lab rows'

    return df_data


def add_hist_deltas(df, cols_num, days, cols_diff):
    # This function calculates the differences between the columns

    # calculate historical deltas
    for col in cols_num:
        for day in days:
            for m in cols_diff:
                df[col + '_' + str(day) + '_' + m + '_DIFF'] = df[col] - df[col + '_' + str(day) + '_' + m]

    cols_hist_delta = [col + '_' + str(day) + '_' + m + '_DIFF' for col in cols_num for day in days for m in cols_diff]

    return df


def sum_window(merge_cols, df_samples, cols_samples, date_samples, \
               df_data, cols_data, date_data, \
               window_days):
    # this function sums the values across the window

    # verify inputs
    check_calc_window(merge_cols, df_samples, cols_samples, date_samples, \
                      df_data, cols_data, date_data)

    # merge the samples on the data
    df = pd.merge(df_samples[list(set(cols_samples + [date_samples]))], df_data, on=merge_cols, how='left')

    # restrict to samples inside the date window
    df = df.loc[(df[date_data] >= (df[date_samples] - pd.to_timedelta(window_days, unit='d'))) & \
                (df[date_data] < (df[date_samples]))]

    # calculate features
    df_sum = df.groupby(cols_samples)[cols_data].sum(axis=0).add_suffix('_%d_COUNT' % window_days)
    # print('df_sum')
    # print(df_sum.head())
    # print('df_samples[cols_samples]')
    # print(df_samples[cols_samples].head())
    # print('cols_samples')
    # print(cols_samples)
    # merge on cols_samples to pick up nans
    df_window = pd.merge(df_samples[cols_samples], df_sum, on=cols_samples, how='left')

    return df_window


def preprocess_sums(merge_cols, df_samples, cols_samples, date_samples, \
                    df_data, cols_data, date_data, \
                    window_days):
    # this function processes the historical sum data into buckets based on window_days
    # Mostly just a wrapper around sum_window
    all_dfs = []
    for w in window_days:
        # add windowing data to the samples
        t1 = time.time()
        print('-Historical window %d...' % w, end='')
        df_window = sum_window(merge_cols, df_samples, cols_samples, date_samples, \
                               df_data, cols_data, date_data, \
                               w)
        all_dfs = all_dfs + [df_window.set_index(cols_samples)]
        t2 = time.time()
        print('done in ', t2 - t1)
    return pd.concat(all_dfs, axis=1).reset_index()


def make_dummies(df, col, my_cats):
    # create fixed one hot encoding columns based on my_cats for the column col in df

    # check schema
    check_schema(df, [col])

    cats = CategoricalDtype(categories=my_cats, ordered=True)
    df[col] = df[col].fillna('UNK')
    df[col] = df[col].astype(cats)
    df_ohe = pd.get_dummies(df[col], prefix=col, drop_first=True)

    return df_ohe
