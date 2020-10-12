# -*- coding: utf-8 -*-
from __future__ import annotations

from copy import deepcopy
from typing import Sequence

import numpy as np

MIN_WH = 0
MIN_MAX = 1
CWH = 2


def min_wh2min_max(bbox: Sequence) -> Sequence:
    bbox[2] += bbox[0]
    bbox[3] += bbox[1]
    return bbox


def min_wh2cwh(bbox: Sequence) -> Sequence:
    bbox[0] += bbox[2] / 2
    bbox[1] += bbox[3] / 2
    return bbox


def cwh2min_wh(bbox: Sequence) -> Sequence:
    bbox[0] -= bbox[2] / 2
    bbox[1] -= bbox[3] / 2
    return bbox


def cwh2min_max(bbox: Sequence) -> Sequence:
    return min_wh2min_max(cwh2min_wh(bbox))


def min_max2min_wh(bbox: Sequence) -> Sequence:
    bbox[2] -= bbox[0]
    bbox[3] -= bbox[1]
    return bbox


def min_max2cwh(bbox: Sequence) -> Sequence:
    return min_wh2cwh(min_max2min_wh(bbox))


_methods = [[lambda x: x] * 3 for _ in range(3)]
_methods[MIN_WH][MIN_MAX] = min_wh2min_max
_methods[MIN_WH][CWH] = min_wh2cwh
_methods[CWH][MIN_WH] = cwh2min_wh
_methods[CWH][MIN_MAX] = cwh2min_max
_methods[MIN_MAX][CWH] = min_max2cwh
_methods[MIN_MAX][MIN_WH] = min_max2min_wh


def transform(
        bbox: Sequence,
        bbox_fmt: int,
        tar_fmt: int,
        inplace: bool = False):
    """
    X_MIN_Y_MIN_WH to X_MIN_Y_MIN_X_MAX_Y_MAX
    Args:
        bbox: bound box
        bbox_fmt: format of bbox
        tar_fmt: target format after transform
        inplace: True for change the bbox, False for generate an new object instead of change the bbox.
    """
    if not inplace:
        bbox = deepcopy(bbox)

    return _methods[bbox_fmt][tar_fmt](bbox)


def calc_iou(box1: Sequence, box2: Sequence, fmt1: int, fmt2: int):
    """
    compute the iou of two boxes.
    Args:
        box1: bound box1
        box2: bound box2
        fmt1: format of bound box1
        fmt2: format of bound box2
    Return:
        iou: iou of box1 and box2.
    See Also:
        BBoxFmt
    """
    x1_min, y1_min, x1_max, y1_max = transform(box1, fmt1, MIN_MAX)
    x2_min, y2_min, x2_max, y2_max = transform(box2, fmt2, MIN_MAX)

    # calculate intersection rectangle's coordinate
    x_i1 = np.max([x1_min, x2_min])
    y_i1 = np.max([y1_min, y2_min])
    x_i2 = np.min([x1_max, x2_max])
    y_i2 = np.min([y1_max, y2_max])

    # calculate two bound boxes' areas
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)

    # calculate intersection area
    inter_area = (np.max([0, x_i2 - x_i1])) * (np.max([0, y_i2 - y_i1]))
    iou = inter_area / (area1 + area2 - inter_area + 1e-6)

    return iou
