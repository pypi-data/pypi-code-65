# -*- coding: utf-8 -*-

def smooth_l1(x):
    """
    Smooth L1 loss defined in Fast R-CNN

    References:
        http://arxiv.org/abs/1504.08083

    """
    return 0.5 * x ** 2 if abs(x) < 1 else abs(x) - 0.5
