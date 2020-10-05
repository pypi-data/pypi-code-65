from functools import wraps

import pandas as pd

from .logging import log


def check_size_variation(logger=None):
    def decorator(func):
        @wraps(func)
        def wrapper(df, *args, **kwargs):
            nb_rows_input = df.shape[0]
            output = func(df, *args, **kwargs)
            nb_rows_output = output.shape[0]
            nb_rows_evolution = (nb_rows_output - nb_rows_input) / nb_rows_input * 100
            log(f'{func.__name__}: {nb_rows_input} -> {nb_rows_output} ({nb_rows_evolution:.1f}%)', logger)
            return output
        return wrapper
    return decorator


def configure_pandas(max_rows=None, max_columns=None, max_width=None, max_colwidth=None, logger=None):
    pd.set_option('display.max_rows', max_rows)
    pd.set_option('display.max_columns', max_columns)
    pd.set_option('display.max_colwidth', max_colwidth)
    pd.set_option('display.width', max_width)
    pd.set_option('display.expand_frame_repr', True)
    log('Pandas options were successfully set', logger=logger)
