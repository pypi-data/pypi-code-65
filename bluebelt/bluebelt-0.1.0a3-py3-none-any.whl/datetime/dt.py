import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from bluebelt.datetime import holidays
from bluebelt.helpers.exceptions import *

# series
def year(series, **kwargs):
    return series.dt.year

def quarter(series, **kwargs):
    return np.ceil(series.dt.month/3).astype(int)

def month(series, **kwargs):
    return series.dt.month

def day(series, **kwargs):
    return series.dt.day

def weekday(series, **kwargs):
    return series.dt.weekday

def day_name(series, **kwargs):
    return series.dt.day_name()

def is_holiday(series, **kwargs):
    return series.apply(lambda x: holidays.holidays(x))

def is_weekend(series, **kwargs):
    weekend_days = kwargs.get('weekend_days', [5, 6])
    return series.apply(lambda x: pd.to_datetime(x).date().weekday() in weekend_days)

def iso_year(series, **kwargs):
    return series.apply(lambda x: x.isocalendar()[0])

def iso_week(series, **kwargs):
    return series.apply(lambda x: x.isocalendar()[1])

def week(series, **kwargs):
    return series.apply(lambda x: x.isocalendar()[1])

# dataframe
def date_from_weeknumber(df,
                         year=None,
                         week=None,
                         day=0,
                         ):


    # data checks
    if isinstance(year, (list, pd.Series, np.ndarray, int, float)) and isinstance(week, (list, pd.Series, np.ndarray, int, float)):
        year = pd.Series(year)
        week = pd.Series(week)
        if year.shape[0] == week.shape[0]:
            df = pd.DataFrame({'year': year, 'week': week})
        else:
            raise InputError("'year' and 'week' need to have equal lengths")
    elif isinstance(df, pd.DataFrame) and isinstance(year, str) and isinstance(week, str):
        df = pd.DataFrame({'year': df[year], 'week': df[week]})
    else:
        raise InputError("arguments not in the right format")

    def weeknum(row, year=None, week=None, day=0):
        d = pd.to_datetime(f'4 jan {row[year]}')  # The Jan 4th must be in week 1 according to ISO
        result =  d + pd.Timedelta(weeks=(row[week])-1, days=-(d.weekday()) + day)
        return result
    
    return df.apply(lambda x: weeknum(x, year=year, week=week, day=day), axis=1)
