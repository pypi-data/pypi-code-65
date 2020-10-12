import unittest

import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, StratifiedKFold

from ddplt.classification import draw_roc_cv, draw_prc_cv, draw_roc_prc_cv
from .test_base import BinaryClassificationTestBase, MulticlassClassificationTestBase

# set this to true if you want to see the plots
interactive = False


class TestClassification(BinaryClassificationTestBase):

    def setUp(self) -> None:
        super(TestClassification, self).setUp()
        self.cv = KFold(n_splits=5, shuffle=True, random_state=123)

    def test_draw_roc_prc_cv(self):
        fig, (l, r) = plt.subplots(1, 2, figsize=(8, 4), dpi=150)
        draw_roc_prc_cv(self.estimator, self.X, self.y, self.cv, roc_ax=l, prc_ax=r)

        if interactive:
            plt.show()

    def test_draw_roc_cv(self):
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        draw_roc_cv(self.estimator, self.X, self.y, self.cv, ax=ax)

        if interactive:
            plt.show()

    def test_draw_prc_cv(self):
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        draw_prc_cv(self.estimator, self.X, self.y, self.cv, ax=ax)

        if interactive:
            plt.show()

    @unittest.skip
    def test_fun(self):
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

        ax.scatter(self.X[:, 0], self.X[:, 1], c=self.y)
        if interactive:
            plt.show()


class TestMulticlassClassification(MulticlassClassificationTestBase):

    def setUp(self) -> None:
        super(TestMulticlassClassification, self).setUp()
        self.estimator = LogisticRegression()

        self.cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=123)

    def test_draw_roc_cv(self):
        # nothing at the moment
        pass
