# -*- coding: utf-8 -*-

import torch

from nn_torch.cv.models.detection.anchors import calc_iou, MIN_MAX, MIN_WH


def test_iou():
    iou = calc_iou(torch.tensor([4, 5, 7, 7]), torch.tensor([5, 6, 10, 10]), fmt1=MIN_MAX, fmt2=MIN_MAX)
    assert (torch.abs(iou - 1 / 12) <= 1e-6).all()

    iou: torch.Tensor = calc_iou(torch.tensor([[1, 1, 2, 2]] * 4), torch.tensor([10, 10, 11, 11]), fmt1=MIN_MAX,
                                 fmt2=MIN_MAX)
    assert (iou <= 1e-6).all().item()

    iou = calc_iou(torch.tensor([4, 5, 3, 2]), torch.tensor([5, 6, 10, 10]), fmt1=MIN_WH, fmt2=MIN_MAX)
    assert (torch.abs(iou - 1 / 12) <= 1e-6).all().item()

    iou = calc_iou(torch.tensor([
        [3, 4, 5, 5], [3, 4, 7, 7],
        [3, 4, 8, 8], [3, 4, 9, 9]
    ]), torch.tensor([3, 4, 6, 6]), fmt1=MIN_WH, fmt2=MIN_WH)
    assert iou.shape == torch.Size([4])
    assert (torch.abs(iou - torch.tensor([25. / 36, 36. / 49, 36. / 64, 36. / 81])) <= 1e-6).all().item()

    iou = calc_iou(torch.tensor([
        [3, 4, 5, 5], [3, 4, 7, 7],
        [3, 4, 8, 8], [3, 4, 9, 9]
    ]), torch.tensor([[3, 4, 6, 6], [3, 4, 1, 1], [3, 4, 8, 8], [3, 4, 8, 8]]), fmt1=MIN_WH, fmt2=MIN_WH)
    assert (torch.abs(iou - torch.tensor([25. / 36, 1. / 49, 1., 64. / 81])) <= 1e-6).all().item()
