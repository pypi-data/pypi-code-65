# -*- coding: utf-8 -*-
from nn_torch.cv.models.detection.anchors import calc_iou, MIN_MAX, MIN_WH


def test_iou():
    iou = calc_iou([4, 5, 7, 7], [5, 6, 10, 10], fmt1=MIN_MAX, fmt2=MIN_MAX)
    assert abs(iou - 1 / 12) <= 1e-6

    iou = calc_iou([1, 1, 2, 2], [10, 10, 11, 11], fmt1=MIN_MAX, fmt2=MIN_MAX)
    assert iou <= 1e-6

    iou = calc_iou([4, 5, 3, 2], [5, 6, 10, 10], fmt1=MIN_WH, fmt2=MIN_MAX)
    assert abs(iou - 1 / 12) <= 1e-6
