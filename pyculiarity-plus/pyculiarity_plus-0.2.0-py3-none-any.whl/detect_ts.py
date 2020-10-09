# -*- coding: utf-8 -*-
from collections import namedtuple
import datetime
import copy

from pandas import DataFrame, to_datetime
from pandas import Timestamp
import numpy as np
from pyculiarity_plus.seasonal.seasonal import fit_seasons, adjust_seasons, rsquared_cv

from pyculiarity_plus.detect_anoms import detect_anoms
from pyculiarity_plus.detect_anoms import detect_anoms


def detect_ts(df, max_anoms=0.10, direction='pos', alpha=0.05, only_last = False, res_season=False, inplace=True, kind='median'):
    """
    Anomaly Detection Using Seasonal Hybrid ESD Test +
    A technique for detecting anomalies in seasonal univariate time series where the input is a
    series of <timestamp, value> pairs.

    Args:

    df: Time series as a two column data frame where the first column consists of the integer UTC Unix
    timestamps and the second column consists of the observations.

    max_anoms: Maximum number of anomalies that S-H-ESD will detect as a percentage of the data.

    direction: Directionality of the anomalies to be detected. Options are: ('pos' | 'neg' | 'both').
    It should be 'neg' for EFTA and 'pos' for Cancellation Rate.

    alpha: The level of statistical significance with which to accept or reject anomalies.

    only_last: Report the anomaly only for the last observation in the time series. Options: (True | False)
    True: day mode. False: window mode.
    
    res_season: seasonality constraint setting. True, set a fixed periodicity to 7 days.
                False, set a minimum periodicity to 7 days.
    
    inplace: replace the orginal data.
    
    Returns: a dataframe with the following columns:
            timestamp,value,expected_value, trend, seasonal,remainder,residue, day_mode, 
            test_time, intime_alert, if_anom, periodicity, tev, fev, country, vertical, metric, width
             
            day_mode: True/False.
            test_time: the last day of the current time window.
            intime_alert: True if timestamp == test_time else False.
    """
    
    # check input parameters
    if not isinstance(df, DataFrame):
        raise ValueError("data must be a single data frame.")
    else:
        if len(df.columns) != 2 or not df.iloc[:, 1].map(np.isreal).all():
            raise ValueError('''data must be a 2 column data.frame, with the first column being a set of timestamps, and
                                the second coloumn being numeric values.''')

        if not (df.dtypes[0].type is np.float64) and not (df.dtypes[0].type is np.int64):
            raise ValueError('''The input timestamp column must be a float or integer of the unix timestamp, not date
                                time columns, date strings or pd.TimeStamp columns.''')

    if not inplace:
        df = copy.deepcopy(df)

    if max_anoms > 0.49:
        length = len(df.value)
        raise ValueError("max_anoms must be less than 50%% of the data points (max_anoms =%f data_points =%s)." % (round(max_anoms * length, 0), length))

    if direction not in ['pos', 'neg', 'both']:
        raise ValueError("direction options are: pos | neg | both.")

    if not (0.01 <= alpha or alpha <= 0.1):
        import warnings
        warnings.warn("alpha is the statistical signifigance, and is usually between 0.01 and 0.1")

    if not isinstance(only_last, bool):
        raise ValueError("only_last must be a boolean")
        
    # change the column names in place
    df.rename(columns={df.columns.values[0]: "timestamp", df.columns.values[1]: "value"}, inplace=True)
    df = df.sort_values(by=['timestamp'])
    # now convert the timestamp column into a proper timestamp
    df['timestamp'] = df['timestamp'].map(lambda x: datetime.datetime.utcfromtimestamp(x))
    
    
    # make sure at leat 1 possible anomaly
    num_obs = len(df.value)
    clamp = (1 / float(num_obs))
    if max_anoms < clamp:
        max_anoms = clamp
        
        
    # decomposition and get the periodicity
    if res_season:
        season, trend = fit_seasons(df.value, period = 7, min_ev = -np.inf, trend=kind)
    else:
        season, trend = fit_seasons(df.value, trend=kind)

    if season is not None:
        period = len(season)
    else: 
        season, trend = fit_seasons(df.value, period = 7, min_ev = -np.inf, trend=kind)
        period = 7
        
    # output container 
    seasonal_plus_trend = DataFrame(columns=['timestamp', 'value', 'expected_value', 'trend', 'seasonal',
                                             'remainder', 'residue'])
    
    Direction = namedtuple('Direction', ['one_tail', 'upper_tail'])
    directions = {
        'pos': Direction(True, True),
        'neg': Direction(True, False),
        'both': Direction(False, True)
    }
    anomaly_direction = directions[direction]
    
    # start anomly detection 
    all_data = [df]
    for i in range(len(all_data)):
        
        # s_h_esd_timestamps: dictionary type
        s_h_esd_timestamps = detect_anoms(all_data[i], k=max_anoms, alpha=alpha,season=season, trend=trend,
                                          one_tail=anomaly_direction.one_tail,
                                          upper_tail=anomaly_direction.upper_tail, only_last=only_last)                         
        if s_h_esd_timestamps is None:
            return None
            
        # organize the result to a dataframe.
        data_decomp = s_h_esd_timestamps['stl']  # trend, seasonal, remainder, residue
        tev = s_h_esd_timestamps['tev']
        fev = s_h_esd_timestamps['fev']
        seasonal_plus_trend = seasonal_plus_trend.append(data_decomp)

        seasonal_plus_trend['day_mode'] = only_last
        seasonal_plus_trend['test_time'] = all_data[i].timestamp.values[-1]

        def f(x):
            if x['timestamp'] == x['test_time']:
                return True
            else:
                return False
        seasonal_plus_trend['intime_alert'] = seasonal_plus_trend.apply(lambda x: f(x), axis=1)
        
        s_h_esd_timestamps = s_h_esd_timestamps['anoms']  # anomaly records
        seasonal_plus_trend['if_anom'] = False
        if s_h_esd_timestamps is not None:
            seasonal_plus_trend['if_anom'] = np.where(seasonal_plus_trend.timestamp.isin(s_h_esd_timestamps), True, False)


        seasonal_plus_trend['periodicity'] = period
        seasonal_plus_trend['tev'] = tev
        seasonal_plus_trend['fev'] = fev

    # timestamps in seasonal_plus_trend now is a str instread of unix time
    return seasonal_plus_trend

