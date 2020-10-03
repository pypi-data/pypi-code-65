from sklearn.feature_selection import VarianceThreshold

doc_string = """
This is a math Module
Do Some thing
"""


def __doc__():
    return doc_string


def get_constant_variance_columns(X, get_non_const_cols=False):
    """
    Get list of columns with constant variance.
    :param X: Independent Variables/Features
    :param get_non_const_cols: If 'True' returns non constant columns, 'False' by default
    :return: List of columns based on constant variance.
    """
    if get_non_const_cols:
        return [column for column in X.columns if column in X.columns[VarianceThreshold(threshold=0).fit(X).get_support()]]
    return [column for column in X.columns if column not in X.columns[VarianceThreshold(threshold=0).fit(X).get_support()]]


def get_multi_collinear_columns(X, threshold=0.8, consider_negative_corr=True):
    """
    Get List of Columns which are collinear to each other
    :param X: Independent Variables/Features
    :param threshold: Threshold value of correlation, default value os 0.8
    :param consider_negative_corr: If 'True' then considers absolute value else -ve correlation in not considered, 'True' by default
    :return: List of collinear columns
    """
    col_corr = set()  # Set of all the names of correlated columns
    corr_matrix = X.corr()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if consider_negative_corr:
                corr_value = abs(corr_matrix.iloc[i, j])
            else:
                corr_value = (corr_matrix.iloc[i, j])

            if corr_value > threshold: # we are interested in absolute coeff value
                col_corr.add(corr_matrix.columns[i]) # getting the name of column
    return col_corr



