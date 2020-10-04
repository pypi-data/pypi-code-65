import sys
import logging
import pandas as pd
import numpy as np


def create_demo_matrix():
    return np.array([i for i in range(20)]).reshape(-1, 2)


def create_demo_df():
    a = create_demo_matrix()
    df = pd.DataFrame(a, columns=['x', 'y'])
    return df


def setup_options():
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html
    pd.set_option('display.width', 5000)
    pd.set_option('display.max_rows', 5000)
    pd.set_option('display.max_colwidth', 5000)
    pd.set_option('max_columns', 600)
    pd.set_option('display.float_format', lambda x: '%.2f' % x)  # disable scientific notation for print

    # https://numpy.org/doc/stable/reference/generated/numpy.set_printoptions.html
    np.set_printoptions(precision=4)
    np.set_printoptions(threshold=sys.maxsize)
    np.set_printoptions(linewidth=5000)
    np.set_printoptions(suppress=False)  # no scientific notation


def get_logger(name, format=None):
    if format is None:
        format='%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s] %(message)s'

    logging.basicConfig(format=format, level=logging.INFO)
    logger = logging.getLogger(name)
    return logger
