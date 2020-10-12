import unittest

from sklearn.datasets import load_iris, make_moons
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC


class TestBase(unittest.TestCase):

    def setUp(self) -> None:
        # import some data to play with
        iris = load_iris()
        self.X = iris.data
        self.y = iris.target
        # self.y_is_setosa = iris.target == 1  # to have a binary classification problem
        self.class_names = iris.target_names
        self.feature_names = iris.feature_names

        # Split the data into a training set and a test set
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, random_state=0)




class BinaryClassificationTestBase(unittest.TestCase):

    def setUp(self) -> None:
        # import some data to play with
        self.X, self.y = make_moons(1_000, noise=.2, random_state=123)

        self.estimator = LogisticRegression()


class MulticlassClassificationTestBase(unittest.TestCase):

    def setUp(self) -> None:
        # import some data to play with
        self.X, self.y = load_iris(return_X_y=True)
