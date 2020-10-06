from unittest import TestCase
from ocr4all_pixel_classifier.lib.evaluation import *


class Test(TestCase):
    def test_count_matches(self):
        self.fail()


class TestConnectedComponentEval(TestCase):
    def test_filter(self):
        mask = np.array([
            [1, 0, 0, 0],
            [1, 0, 2, 2],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
        ])
        pred = np.array([
            [2, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 2, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
        ])
        bin = np.array([
            [1, 0, 0, 0],
            [1, 0, 1, 1],
            [1, 0, 0, 0],
            [1, 0, 1, 1],
            [1, 0, 0, 0],
            [1, 0, 1, 1],
        ])
        cc1 = np.array([
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
        ])
        cc2 = np.array([
            [0, 0, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ])
        cc3 = np.array([
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ])
        cc4 = np.array([
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 1],
        ])

        cce = ConnectedComponentEval(mask, pred, bin, connectivity=4).only_label(2, 0.5)
        cce._filter(cc1)

        pass
