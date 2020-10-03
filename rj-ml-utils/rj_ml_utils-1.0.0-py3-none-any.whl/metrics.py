import numpy as np
from sklearn import metrics  # Importing metrics from SK-Learn

doc_string = """
Metrics module to evaluate models
"""


def __doc__():
    return doc_string


def regression_model_evaluation(y, y_predict, set_type='', features_count=None):
    """
    Utility/Helper method to calculate the evaluation parameters for a regression model
    """
    result = {}

    if set_type != '':
        set_type = '_' + set_type

    # Mean Absolute Error on train set.
    result['MAE'] = metrics.mean_absolute_error(y, y_predict)
    # Mean Squared Error on train set.
    result['MSE'] = metrics.mean_squared_error(y, y_predict)
    # Root Mean Squared Error on train set.
    result['RMSE'] = np.sqrt(result['MSE'])
    # R_squared on train set.
    result['R_squared'] = metrics.r2_score(y, y_predict)

    # Adj r2 = 1-(1-R2)*(n-1)/(n-p-1)
    if features_count:
        # Adjusted R_squared on train set.
        result['Adj_R_squared'] = 1 - (
                ((1 - result['R_squared']) * (len(y) - features_count)) / (len(y) - features_count - 1))
    # Returning with appending type to key and rounding value
    return {f'{k}' + set_type: round(v, 4) for k, v in result.items()}
