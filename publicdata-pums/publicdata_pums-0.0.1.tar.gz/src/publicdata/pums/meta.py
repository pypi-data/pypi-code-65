# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT License, included in this distribution as LICENSE

from .exceptions import PumsError
from functools import lru_cache
import numpy as np
import pandas as pd

def dd_url(year, release):

    if year < 2014:
        raise PumsError('Metadata only available for 2014 or later. ')

    year = int(year)
    release = int(release)
    if release == 5:
        yr = f"{year-4}-{year}"
    else:
        yr = str(year)

    if year == 2016 and release == 1:
        return 'https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict16.txt'
    else:
        return f'https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_{yr}.txt'

@lru_cache(None)
def get_dd(year, release):
    import requests

    text = requests.get(dd_url(year, release)).text

    return text.splitlines()


def parse_meta(year, release):
    import re

    sl_pat = re.compile(r'^([A-Z0-9]+)\s+(\w+)?\s*(\d+)')
    labels_pat = re.compile(r'^\s+([^\s]+)\s+(.*)')

    state = None
    labels = []
    col_desc = None
    col_name = None

    rows = []

    for l in get_dd(year, release):

        if not l.strip() or l.strip().startswith('NOTE'):
            continue

        m = sl_pat.match(l)
        if m:

            state = 'col_desc'

            if col_name:
                rows.append((col_name, col_desc, length, list(labels)))

            col_name, dtype, length = m.group(1), m.group(2), m.group(3)

            labels = []
            col_desc = ''
            continue

        if state == 'col_desc':
            col_desc = l
            state = 'labels'
            continue

        m = labels_pat.match(l)
        if m:
            labels.append((m.group(1), m.group(2)))
            continue

    return rows

def category_map(year, release):
    rows = parse_meta(year, release)

    cm = {}

    def try_int(v):
        try:
            return int(v)
        except:
            if str(v)[0] == 'b':
                return np.nan
            else:
                return v

    for r in rows:
        cm[r[0]] = { try_int(val):label for val, label in r[3]}

    return cm

def categorize(df, cm):
    """Convert a dataframe or series to use categoricals"""

    def has_int_keys(m):
        return any(isinstance(k, int) for k in m.keys())

    def categorize_s(s, mp):
        if not has_int_keys(mp):
            return s
        else:
            return s.astype('category').cat.rename_categories(mp)

    if isinstance(df, pd.DataFrame):
        for col, mp in cm.items():
            if col in df.columns:
                df[col] = categorize_s(df[col], mp)
        return df
    else:
        # It should be a series
        mp = cm.get(df.name)
        return categorize_s(df, mp)


def dd_html(year, release):
    """Return an HTML table for the metadata for the table. excludes replicate weights. """
    import re

    rows = parse_meta(year, release)
    link = f"<p><a target=\"_blank\" href=\"{dd_url(year, release)}\">Full Data Dictionary for year {year}, release {release}</a></p>"

    pw_pat = re.compile(r'PWGTP\d+|WGTP\d+')
    tr = [f"<tr><td>{i}</td><td>{r[0]}</td><td>{r[1]}</td></tr>" for i, r in enumerate(rows) if not pw_pat.match(r[0])]

    return  f"{link}<table><tr><th>#</th><th>Column Name</th><th>Description</th></tr>{''.join(tr)}</table>"

def dd_repr_html(year, release):
    """Display data distionary in an Jupyter notebook. """
    from IPython.display import HTML

    return HTML(dd_html(year, release))
