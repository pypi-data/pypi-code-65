"""Module for preprocessing data
"""

import math

import numpy as np
import pandas as pd
from sklearn import preprocessing


def normalize_all_data(data):
    """Normalize data by scaling to get 0 mean and 1 standard deviation

    Args:
        data (DataFrame/ndarray) -- Data to be normalised

    Returns:
        n_data (DataFrame/ndarray) -- Normalized data
        normalizer (StandardScaler) -- Instance of transformer class,
            can be stored and used later
    """

    if isinstance(data, pd.DataFrame):
        n_data = data.values

        normalizer = preprocessing.MinMaxScaler().fit(n_data)
        n_data = normalizer.transform(n_data)

        return pd.DataFrame(data=n_data,
                            columns=data.columns,
                            index=data.index), normalizer

    if not isinstance(data, np.ndarray):
        raise ValueError(
            "Expected ndarray or dataframe got {} for data".format(type(data)))

    n_data = data

    normalizer = preprocessing.MinMaxScaler().fit(n_data)
    n_data = normalizer.transform(n_data)

    return n_data, normalizer


def convert_to_column(dataframe, window_size, stride=-1):
    """Converts input data in sets of window_size to stacked column vectors

    Args:
        dataframe (DataFrame/ndarray) -- Input dataframe to convert to column
        window_size (+ve int) -- Number of timesteps in one column
        stride (int, optional) -- Length of each stride, timesteps between
            start of consecutive frames, non zero, less than window_size.
            Defaults to -1.

    Returns:
       transformed_data (DataFrame) -- Data after conversion
    """

    if stride == 0:
        raise ValueError(
            "Invalid stride: {}! Expected non-zero input".format(stride))

    if window_size <= 0:
        raise ValueError(
            "Invalid window size: {}! Expected positive integer".format(
                window_size))

    if stride > window_size:
        raise ValueError("Stride must be less than window_size for overlap")

    if stride < 0:
        stride = window_size + 1 + stride
        # Happens when stride is more negative than -(window_size + 1)
        if stride <= 0:
            raise ValueError(
                "Stride too negative! Stride must be between"
                " -(window_size + 1) and window_size both inclusive.")

    if isinstance(dataframe, pd.DataFrame):
        data = dataframe.to_numpy()
    else:
        data = dataframe

    n_rows, n_columns = data.shape

    n_t = math.ceil((n_rows - window_size) / stride) + 1  # No. of new windows

    # Example ################################################################
    # n_rows      =  8
    # stride      =  2
    # window_size =  5
    # 0 1     -
    # 1 1      | -> Multiple of stride number of rows
    # 2 1 2    |
    # 3 1 2   -
    # 4 1 2 3 -
    # 5   2 3  | -> Ignore this window_size number rows (Since it is the last
    # 6   2 3  |    one there will be extra rows here which are used but not
    # 7     3  |    a multiple of stride)
    # 8     3 -
    # 9

    # If you take the remaining rows and take modulo with stride, you should
    # get the number of unused rows

    # n_rows - window_size = 10 - 5 = 5
    # modulo stride = 5 % 2 = 1 = unused_rows
    # End Example ############################################################

    unused_rows = (n_rows - window_size) % stride
    if unused_rows != 0:
        buffer_rows = stride - unused_rows
    else:
        buffer_rows = 0

    # Pad the data to get the number of rows we need. This means that no
    # data is thrown out the window
    local_data = np.zeros((n_rows + buffer_rows, n_columns))
    local_data[:n_rows, :] = data

    transformed_data = np.zeros((n_t, n_columns * window_size))

    # Create the new rows from the existing ones
    for i in range(n_t):
        start_index = i * stride
        end_index = start_index + window_size
        # using vectorized methods instead of for loops
        transformed_data[i, :] = local_data[start_index:end_index, :].reshape(
            (1, -1))

    transformed_data = pd.DataFrame.from_records(transformed_data)

    if isinstance(dataframe, pd.DataFrame):
        column_names = []
        for i in range(window_size):
            column_names += [
                str(column_name) + str(i) for column_name in dataframe.columns
            ]
        transformed_data.columns = column_names

    return transformed_data


def convert_from_column(dataframe, window_size, stride=-1):
    """Converts input data to sets of window_size

    Args:
        dataframe (DataFrame/ndarray) -- Input dataframe to convert to column
        window_size (+ve int) -- Number of timesteps in one column
        stride (int, optional) -- Length of each stride, timesteps between
            start of consecutive frames, non zero. Defaults to -1.

    Returns:
       transformed_data (DataFrame) -- Data after conversion
    """

    if stride == 0:
        raise ValueError(
            "Invalid stride: {}! Expected non-zero input".format(stride))

    if window_size <= 0:
        raise ValueError(
            "Invalid window size: {}! Expected positive integer".format(
                window_size))

    if stride < 0:
        stride = window_size + 1 + stride
        # Happens when stride is more negative than -(window_size + 1)
        if stride <= 0:
            raise ValueError("Stride too negative!!")

    if isinstance(dataframe, pd.DataFrame):
        data = dataframe.to_numpy()
    else:
        data = dataframe

    n_rows, n_columns = data.shape

    # since window_size number of rows make up one single row.
    n_new_cols = (n_columns) // window_size

    transformed_data = []

    # Fill the list up with data from all but last row
    for i in range(n_rows - 1):
        transformed_data += data[i].reshape((-1, n_new_cols)).tolist()[:stride]

    # Add the last row of data (this row might include buffer_rows introduced
    # by convert_to_column. Such "buffer rows" are not removed!)
    transformed_data += data[n_rows - 1].reshape((-1, n_new_cols)).tolist()

    transformed_data = pd.DataFrame.from_records(transformed_data)

    # Add the column header for the new columns
    if isinstance(dataframe, pd.DataFrame):
        transformed_data.columns = dataframe.columns[:n_new_cols]
    return transformed_data
