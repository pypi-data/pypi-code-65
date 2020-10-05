import numpy as np


def predict_with_threshold(clf, df, threshold):
    """
    Perform class prediction with given trained binary classifier and threshold
    :param clf: binary classifier to be used
    :param df: input dataframe to predict on
    :param threshold: threshold to be used for classification
    :return: the classes predicted
    """
    # Assert threshold value is valid
    assert 0 < threshold < 1, 'Your threshold must be in interval ]0,1['
    # Use the model to predict probabilities
    y_prob = clf.predict_proba(df)[:, 1]
    # Choose a class based on the probabilities and the threshold
    return np.abs(np.round(y_prob - (threshold - 0.5)))  # Cut-off moved from 0.5 to threshold
