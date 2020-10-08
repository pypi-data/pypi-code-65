import pandas as pd
from zla_utilities import \
    db_connector as dbcon, utility as ut
import warnings
warnings.filterwarnings("ignore")

def get_data(msql):
    db = 'partsdatabase'
    df = dbcon.opendata(msql, db)
    return df

def merge_data(df1,df2):
    df3 = df1.set_index(['date', 'customerid']).join(df2.set_index(['date', 'customerid']), lsuffix='_frnt',rsuffix='_serv', how='outer').fillna(0)
    df3['qty'] = df3['qty_frnt'] + df3['qty_serv']
    df3 = df3[['qty']].reset_index()
    return df3

def to_number(df, _by):
    _data = df[['date', 'qty']].groupby('date').sum()
    _data.index = pd.to_datetime(_data.index, format='%Y-%m-%d')
    _data = ut.full_daterange(_data, by=_by)
    return _data