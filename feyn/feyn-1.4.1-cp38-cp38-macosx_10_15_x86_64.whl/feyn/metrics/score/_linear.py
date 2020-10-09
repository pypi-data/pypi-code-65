"""Code for operations involving linear models and assumptions."""
# from __future__ import annotations # PEP 563
# TODO: Where should this be placed? calculate_pc belongs here, but MVL not so much.

import numpy as np

from typing import Union


def calculate_pc(X:np.ndarray, Y:np.ndarray) -> float:
    """ Calculate the Pearson correlation coefficient
    for data sampled from two random variables X and Y.

    Arguments:
        X {np.ndarray} -- First 1D vector of random data.
        Y {np.ndarray} -- First 1D vector of random data.

    Returns:
        float -- The correlation coefficient.
    """    

    n = len(X)

    x_bar = np.mean(X)
    y_bar = np.mean(Y)

    cov_xy = np.sum((X - x_bar) * (Y - y_bar))
    cov_xy = cov_xy / (n-1)

    return cov_xy / (np.std(X) * np.std(Y))


class MultiVariateLinear:
    """ Simple multi-variate linear regression model.
    """

    def fit(self, X_train:np.ndarray, y_train:np.ndarray, sample_weights:np.ndarray=None) -> "MultiVariateLinear":
        """
        Fit the linear model using training data and a target output.
        The weights and bias are stored in self.w. The bias is self.w[0].

        Arguments:
            X_train {np.ndarray} -- The training data. Columns are features and rows
                                    are samples.
            y_train {np.ndarray} -- The target output.

        Keyword Arguments:
            sample_weights {np.ndarray} -- Sample weights for X_train. (default: {None})

        Returns:
            MultiVariateLinear -- Returns a MultiVariateLinear instance with learned weights.
        """
        if sample_weights is None:
            K = np.identity(len(y_train))
        else:
            K = sample_weights

        X_train = self.add_intercept(X_train)
        self.X_train_ = (X_train.T @ K) @ X_train
        self.y_train = (X_train.T @ K) @ y_train

        self.w = np.linalg.inv(self.X_train_) @ self.y_train

        return self

    def predict(self, X_input:np.ndarray) -> Union[np.ndarray, float]:
        """ Predict on input data given in X_input

        Arguments:
            X_input {np.ndarray} -- The input data. Columns are features and rows
                                    are samples.

        Returns:
            np.ndarray -- The output vector or single float of predictions.
        """
        X_input = self.add_intercept(X_input)
        return np.dot(X_input, self.w)

    @staticmethod
    def add_intercept(X:np.ndarray) -> np.ndarray:
        """
        Function for adding a value corresponding to the intercept
        in the training data.

        Arguments:
            X {np.ndarray} -- Data array we will add the intercept column to.
                              Columns are features and rows are samples.
                              If 1D, a single one will be inserted at the
                              beginning of the array.

        Returns:
            np.ndarray -- X with a column of ones added as index 0 along axis 1.
        """
        if len(X.shape) == 1:
            return(np.insert(X, 0, 1))

        return np.insert(X, 0, 1, axis=1)
