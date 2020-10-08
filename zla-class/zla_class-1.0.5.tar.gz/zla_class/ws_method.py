import pandas as pd
from zla_utilities import \
    db_connector as dbcon, utility as ut
import warnings
warnings.filterwarnings("ignore")

def get_data(msql):
    db = 'partsdatabase'
    df = dbcon.opendata(msql, db)
    return df


def to_number(df, _by):
    _data = df[['deldate', 'qty']].groupby('deldate').sum()
    _data.index = pd.to_datetime(_data.index, format='%Y-%m-%d')
    _data = ut.full_daterange(_data, by=_by)
    return _data
