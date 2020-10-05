""" Generate 2D Embeddings """

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

import numpy as np
from lightly import is_sklearn_available
if is_sklearn_available():
    import sklearn.decomposition as decomposition


class PCA(object):
    """Handmade PCA to prevent sklearn dependency

    """

    def __init__(self, n_components=None):
        self.n_components = n_components
        self.mean = None
        self.w = None
        self.eps = 1e-10

    def fit(self, X):
        """Fit PCA to data in X

        Args:
            X: (np.array) N x D array of datapoints

        Returns:
            PCA object to transform datapoints

        """
        X = X.astype(np.float32)
        self.mean = X.mean(axis=0)
        X = X - self.mean + self.eps
        cov = np.cov(X.T) / X.shape[0]
        v, w = np.linalg.eig(cov)
        idx = v.argsort()[::-1]
        v, w = v[idx], w[:, idx]
        self.w = w
        return self

    def transform(self, X):
        """Use PCA to transform data in X

        Args:
            X: (np.array) N x D array of datapoints

        Returns:
            Array of N x P datapoints where P <= D

        """
        X = X.astype(np.float32)
        X = X - self.mean + self.eps
        return X.dot(self.w)[:, :self.n_components]


def fit_pca(embeddings, n_components=2, fraction=None):
    """Fit PCA to randomly selected subset of embeddings

    Args:
        embeddings: (np.array) 2D array of embeddings with shape N x D
        n_components: (int) number of components to keep
        fraction: (float) fraction (in (0, 1]) of the dataset

    Returns:
        A transformer which can be used to transform embeddings
        to lower dimensions
    """
    N = embeddings.shape[0]
    n = N if fraction is None else min(N, int(N * fraction))
    X = embeddings[np.random.permutation(N)][:n]
    if is_sklearn_available():
        return decomposition.PCA(n_components=n_components).fit(X)
    else:
        return PCA(n_components=n_components).fit(X)
