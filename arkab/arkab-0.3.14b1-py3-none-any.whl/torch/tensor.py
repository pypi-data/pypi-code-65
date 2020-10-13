"""Extended tools for tensor"""
import torch as th
from torch import Tensor

__all__ = ['zero_count', 'zero_index']


def zero_count(t: Tensor):
    """
    Count zero item count.
    Args:
        t: source tensor

    Returns:
        count of zero in tensor t
    """
    return (t == 0).sum().item()


def zero_index(t: Tensor, as_index: bool):
    """
    Return zero indexes

    :param t: source tensor
    :param as_index: if true, the return result can be use as index of a tensor
    :return: all zero index of t
    """
    return (t == 0).nonzero(as_tuple=as_index)
