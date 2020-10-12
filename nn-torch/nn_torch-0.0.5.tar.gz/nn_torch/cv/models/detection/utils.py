# -*- coding: utf-8 -*-
from enum import IntEnum
from typing import Union

import numpy as np
import torch


class BBoxFmt(IntEnum):
    """
    Bound box format enums.
    """
    X_MIN_Y_MIN_WH = 0
    X_MIN_Y_MIN_X_MAX_Y_MAX = 1
    X_C_Y_C_WH = 2


def calc_iou(box1: Union[np.ndarray, torch.Tensor, list],
             box2: Union[np.ndarray, torch.Tensor, list],
             fmt: BBoxFmt):
    """
    compute the iou of two boxes.
    Args:
        box1: bound box1
        box2: bound box2
        fmt: format of bound box
    Return:
        iou: iou of box1 and box2.
    """
    if fmt == BBoxFmt.X_MIN_Y_MIN_X_MAX_Y_MAX:
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
    elif fmt == BBoxFmt.X_C_Y_C_WH:
        x1_min, y1_min = box1[0] - box1[2] / 2, box1[1] - box1[3] / 2
        x1_max, y1_max = box1[0] + box1[2] / 2, box1[1] + box1[3] / 2
        x2_min, y2_min = box2[0] - box2[2] / 2, box2[1] - box2[3] / 2
        x2_max, y2_max = box2[0] + box2[2] / 2, box2[1] + box2[3] / 2
    elif fmt == BBoxFmt.X_MIN_Y_MIN_WH:
        x1_min, x2_min = box1[0], box2[0]
        y1_min, y2_min = box1[1], box2[1]
        x1_max, x2_max = x1_min + box1[2], x2_min + box2[2]
        y1_max, y2_max = y1_min + box1[3], y2_min + box2[3]
    else:
        raise ValueError('fmt not implemented')

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
