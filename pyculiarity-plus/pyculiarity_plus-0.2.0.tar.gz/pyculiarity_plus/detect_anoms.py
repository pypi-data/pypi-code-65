from itertools import groupby
from math import sqrt

from future.utils import lmap, lrange
from scipy.stats import t as student_t
from statsmodels.robust.scale import mad
import numpy as np
import pandas as ps
from pyculiarity_plus.seasonal.seasonal import fit_seasons, adjust_seasons, rsquared_cv


def detect_anoms(data, k=0.49, alpha=0.05, season=None, trend=None,
                 one_tail=True, upper_tail=True, only_last = False):
    """
    # Detects anomalies in a time series using S-H-ESD +.
    #
    # Args:
    #	 data: Time series to perform anomaly detection on.
    #	 k: Maximum number of anomalies that S-H-ESD will detect as a percentage of the data.
    #	 alpha: The level of statistical significance with which to accept or reject anomalies.
    #	 one_tail: If TRUE only positive or negative going anomalies are detected depending on if upper_tail is TRUE or FALSE.
    #	 upper_tail: If TRUE and one_tail is also TRUE, detect only positive going (right-tailed) anomalies. If FALSE and one_tail is TRUE, only detect negative (left-tailed) anomalies.
    #.   only_last: Report the anomaly only for the last observation in the time series. Options: (True | False). True: day mode. False: window mode.
    # Returns:
    #   A dictionary containing the anomalies (anoms) and decomposition components (stl).
    """

    if list(data.columns.values) != ["timestamp", "value"]:
        data.columns = ["timestamp", "value"]

    # run length encode result of isnull, check for internal nulls
    if (len(lmap(lambda x: x[0], list(groupby(ps.isnull(
            ps.concat([ps.Series([np.nan]),
                       data.value,
                       ps.Series([np.nan])])))))) > 3):
        raise ValueError("Data contains non-leading NAs. We suggest replacing NAs with interpolated values (see na.approx in Zoo package).")
    else:
        data = data.dropna()
        
    num_obs = len(data)
    data = data.set_index('timestamp')

    true_value = data.value
    detrended = data.value - trend
    
    # there should be fluctuation in a time series.
    if data.value.var()==0:
        return None
                
    tev = 1.0 - detrended.var() / data.value.var() # eev

    # Remove the seasonal component, and the median of the data to create the univariate remainder
    if season is not None:
        fev = rsquared_cv(detrended, len(season))
        season, deseasoned = adjust_seasons(data.value, trend=trend, seasons=season)
        ev = season + data.value.median() # expected_value

    else:
        deseasoned = data.value
        fev = 0
        ev = data.value.median()

        season = 0
        
    # remainder
    d = {
        'timestamp': data.index,
        'value': deseasoned - data.value.median()
    }
    data = ps.DataFrame(d)


    p = {
        'timestamp': data.index,
        'value': true_value,
        'expected_value': ev,
        'trend': trend,
        'seasonal': season,
        'remainder': (data['value']), # R= X - S - median
        'residue': deseasoned - trend, # R= X - T - S
    }
    data_decomp = ps.DataFrame(p)

    # Maximum number of outliers that S-H-ESD can detect (e.g. 49% of data)
    max_outliers = int(num_obs * k)

    # Define values and vectors.
    n = len(data.timestamp)
    R_idx = lrange(max_outliers)

    num_anoms = 0
    
    # statistical tests start. 
    # see for details: https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h3.htm
    # Compute test statistic until r = max_outliers  of values have been removed from the sample.
    # window mode
    if only_last == False:
        for i in lrange(1, max_outliers + 1):
            if one_tail:
                if upper_tail:
                    ares = data.value - data.value.median()
                else:
                    ares = data.value.median() - data.value
            else:
                ares = (data.value - data.value.median()).abs()

            # protect against constant time series
            data_sigma = mad(data.value)  # Compute MAD: median(x-x_median)
            # data_sigma = mad(data.value)*1.4826

            if data_sigma == 0:
                break

            ares /= float(data_sigma)
            R = ares.max()
            temp_max_idx = ares[ares == R].index.tolist()[0]
            R_idx[i - 1] = temp_max_idx
            data = data[data.index != R_idx[i - 1]]  # remove max remainder from data

            if one_tail:
                p = 1 - alpha / float(n - i + 1)

            else:
                p = 1 - alpha / float(2 * (n - i + 1))

            t = student_t.ppf(p, (n - i - 1))
            lam = t * (n - i) / float(sqrt((n - i - 1 + t**2) * (n - i + 1)))

            if R > lam:
                num_anoms = i

        if num_anoms > 0:
            R_idx = R_idx[:num_anoms]
        else:
            R_idx = None


    # day mode
    else:
        last_date = data.index[-1]
        alt = False    # True if the last observation is an anomaly.
        pick = False   # True if the last observation is picked.

        for i in lrange(1, max_outliers + 1):
            if one_tail:
                if upper_tail:
                    ares = data.value - data.value.median()
                else:
                    ares = data.value.median() - data.value
            else:
                ares = (data.value - data.value.median()).abs()

            # protect against constant time series
            data_sigma = mad(data.value)  # Compute MAD: median(x-x_median)
            if data_sigma == 0:
                break
            ares /= float(data_sigma)

            R = ares.max()
            temp_max_idx = ares[ares == R].index.tolist()[0]
            R_idx[i - 1] = temp_max_idx

            data = data[data.index != R_idx[i - 1]]  # remove max remainder from data

            if temp_max_idx == last_date:
                pick = True
                if one_tail:
                    p = 1 - alpha / float(n - i + 1)
                else:
                    p = 1 - alpha / float(2 * (n - i + 1))
                t = student_t.ppf(p, (n - i - 1))
                lam = t * (n - i) / float(sqrt((n - i - 1 + t ** 2) * (n - i + 1)))

                if R > lam:
                    alt = True
                    break
                else:
                    continue

            if pick == True:
                if one_tail:
                    p = 1 - alpha / float(n - i + 1)
                else:
                    p = 1 - alpha / float(2 * (n - i + 1))
                t = student_t.ppf(p, (n - i - 1))
                lam = t * (n - i) / float(sqrt((n - i - 1 + t ** 2) * (n - i + 1)))

                if R > lam:
                    alt = True
                    break

        if alt:
            return {'anoms': [last_date], 'stl': data_decomp,'tev':tev,'fev': fev}
        else:
            return {'anoms': None,'stl': data_decomp,'tev':tev,'fev': fev}

    return {
        'anoms': R_idx,
        'stl': data_decomp,
        'tev':tev,
        'fev': fev
    }
