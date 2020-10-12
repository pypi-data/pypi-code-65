# -*- coding: utf-8 -*-
from nn_torch.cv.models.detection.utils import calc_iou, BBoxFmt


def test_iou():
    iou = calc_iou([4, 5, 7, 7], [5, 6, 10, 10], fmt=BBoxFmt.X_MIN_Y_MIN_X_MAX_Y_MAX)
    assert abs(iou - 1 / 12) <= 1e-6

    iou = calc_iou([1, 1, 2, 2], [10, 10, 11, 11], fmt=BBoxFmt.X_MIN_Y_MIN_X_MAX_Y_MAX)
    assert iou <= 1e-6
