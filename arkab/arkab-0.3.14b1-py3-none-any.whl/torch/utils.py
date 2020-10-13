import torch
from torch import autograd
import numpy as np
from torch import nn
from functools import partial
import math
from typing import Literal, Union, Callable, List


def to_scalar(var):
    """
    返回 python 浮点数 (float)
    """
    return var.view(-1).data.tolist()[0]


def argmax(vec):
    """
    以 python 整数的形式返回 argmax
    Args:
        vec: tensor type

    Returns:

    """
    _, idx = torch.max(vec, 1)
    return to_scalar(idx)


def log_sum_exp(vec):
    """
    使用数值上稳定的方法为前向算法计算指数和的对数
    Args:
        vec: PyTorch Tensor type vector

    Returns:

    """
    max_score = vec[0, argmax(vec)]
    max_score_broadcast = max_score.view(1, -1).expand(1, vec.size()[1])
    return max_score + torch.log(torch.sum(torch.exp(vec - max_score_broadcast)))


def calc_cnn_hw(shape: tuple, kernel: Union[tuple, int] = 1,
                padding: Union[tuple, int] = 0,
                dilation: Union[tuple, int] = 1,
                stride: Union[tuple, int] = 1):
    hi, wi = shape
    if isinstance(kernel, tuple):
        kh, kw = kernel
    else:
        kh = kernel
        kw = kernel
    if isinstance(padding, tuple):
        ph, pw = padding
    else:
        ph = pw = padding
    if isinstance(dilation, tuple):
        dh, dw = dilation
    else:
        dh = dw = dilation
    if isinstance(stride, tuple):
        sht, sw = stride
    else:
        sht = stride
        sw = stride
    ho = math.floor((hi + 2 * ph - dh * (kh - 1) - 1) / sht + 1)
    wo = math.floor((wi + 2 * pw - dw * (kw - 1) - 1) / sw + 1)
    return ho, wo


AGGR = Literal['nil', 'sum', 'flat']


def calc_cnn_stack(inputs: tuple, call_chain: List[Callable], aggr: AGGR = 'flat'):
    h, w = inputs
    for c in call_chain:
        h, w = c(shape=(h, w))
    if aggr == 'nil':
        return h, w
    elif aggr == 'sum':
        return h + w
    else:
        # flat
        return h * w
