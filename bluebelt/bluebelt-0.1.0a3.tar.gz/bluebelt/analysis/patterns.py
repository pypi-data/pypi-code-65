from bluebelt.helpers.text import get_nice_polynomial_name

import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.stats as stats

import warnings

def polynomial(series, shape=(0, 6), validation='p_val', threshold=0.05):

    """
    Find the polynomial of a series.
    series = the pandas Series
    shape: int or tuple
        when an int is provided the polynomial is provided as n-th degree polynomial
        when a tuple is provided the function will find an optimised polynomial between first and second value of the tuple
    validation: only for tuple shape
        p_val: test for normal distribution of the residuals
        rsq: check for improvement of the rsq value
    threshold: the threshold for normal distribution test or rsq improvement
    """

    # get the index
    index = series.index.astype(int)-series.index.astype(int).min()
    index = index / np.gcd.reduce(index)

    # drop nan values
    _index = series.index.dropna().astype(int)-series.index.astype(int).min()
    _index = _index / np.gcd.reduce(_index)

    # get the values
    values = series.dropna().values

    # set first rsq
    _rsq = 0


    if isinstance(shape, int):
        result = pd.Series(index=series.index, data=poly.polyval(index, poly.polyfit(_index, values, shape)), name=f'{get_nice_polynomial_name(shape)}')

    elif isinstance(shape, tuple):

        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            for shape in range(shape[0], shape[1]+1):
                try:
                    result = pd.Series(index=series.index, data=poly.polyval(index, poly.polyfit(_index, values, shape)), name=f'{get_nice_polynomial_name(shape)}')
                    residuals = pd.Series(index=series.index, data=[a - b for a, b in zip(values, result)])
                    
                    np_err = np.seterr(divide='ignore', invalid='ignore') # ignore possible divide by zero
                    rsq = np.corrcoef(series.values, result.values)[1,0]**2
                    np.seterr(**np_err) # go back to previous settings
                    
                    p_val = stats.mstats.normaltest(residuals.values)[1]

                    if validation=='p_val' and p_val >= threshold:
                        break
                    elif validation=='rsq' and (rsq - _rsq) / rsq < threshold:
                        result = pd.Series(index=series.index, data=poly.polyval(index, poly.polyfit(_index, values, shape-1)), name=f'{get_nice_polynomial_name(shape-1)}')    
                        break
                    
                    # set previous rsq
                    _rsq = rsq

                except poly.pu.RankWarning:
                    print(f'RankWarning at {get_nice_polynomial_name(shape)}')
                    break
    else:
        result = None

    return result

def periodical(series, period='1W', how=None, **kwargs):

    if how=='min':
        result = series.resample(rule=period, label='left').min().reindex_like(series, method='ffill')
    elif how=='max':
        result = series.resample(rule=period, label='left').max().reindex_like(series, method='ffill')
    elif how=='std':
        result = series.resample(rule=period, label='left').std().reindex_like(series, method='ffill')
    else:
        result = series.resample(rule=period, label='left').mean().reindex_like(series, method='ffill')

    if kwargs.get('step'):
        result = result.divide(kwargs.get('step')).round(0).multiply(kwargs.get('step'))
    
    return result

def anomalies(df=None, values=None, pattern=None, sigma=2):
    """
    pass a DataFrame and two strings with the column names or
    two series for values or pattern
    """

    # dataframe or series
    if df is not None:
        values = df[values]
        pattern = df[pattern]

    residuals = pd.Series(index=values.index, data=[a - b for a, b in zip(values, pattern)])

    return pd.Series(index=values.index, data=(residuals.abs() > (residuals.std() * sigma)))
