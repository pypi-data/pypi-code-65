# -*- coding: UTF-8 -*-
""""
Created on 02.11.2019
This module contains utils for pytorch.

:author:     Martin Dočekal
"""
import copy
import itertools
from collections import Set
from typing import Any, Iterator, Tuple, Iterable, Union
from abc import ABC, abstractmethod
import torch


def batch_tril_set(t: torch.tensor, val: Any = 0, diagonal: bool = True, inPlace: bool = False) -> torch.tensor:
    """
    Sets each element of lower triangular of batch tensors to given value.

    :param inPlace:
    :type inPlace:
    :param t: Three dimensional tensor of size BATCH_SIZE X A X B.
    :type t: torch.tensor
    :param val: Value that should be set.
    :type val: Any
    :param diagonal: True means that diagonal should be set too. False otherwise.
    :type diagonal: bool
    :param inPlace: If true than works in place.
    :type inPlace: bool
    :return: Changed tensor with new values. If inPlace is False than this is cloned vector with new values, else
    it is the same vector with new values.
    :rtype: torch.tensor
    """
    if not inPlace:
        t = t.clone()
    for batchI in t:
        for row in range(0 if diagonal else 1, batchI.shape[0]):
            batchI[row][:row + diagonal] = val

    return t


def batch_triu_set(t: torch.tensor, val: Any = 0, diagonal: bool = True, inPlace: bool = False) -> torch.tensor:
    """
    Sets each element of upper triangular of batch tensors to given value.

    :param t: Three dimensional tensor of size BATCH_SIZE X A X B.
    :type t: torch.tensor
    :param val: Value that should be set.
    :type val: Any
    :param diagonal: True means that diagonal should be set too. False otherwise.
    :type diagonal: bool
    :param inPlace: If true than works in place.
    :type inPlace: bool
    :return: Changed tensor with new values. If inPlace is False than this is cloned vector with new values, else
    it is the same vector with new values.
    :rtype: torch.tensor
    """
    if not inPlace:
        t = t.clone()
    for batchI in t:
        for row in range(0, batchI.shape[0]):
            batchI[row][row + (not diagonal):] = val

    return t


def span_mask(tensorLen: int, maxSpanSize: int) -> torch.tensor:
    """
    Generates index mask for all possible spans of given span size for given tensor length.
    Span in this context is just consisting from start and end elements, as shown in the example.

    Example:
        t = tensor([4 5 6 7])
        M = spanMask(t.shape[0], 3)
            tensor([
             [0, 0], [0, 1], [0, 2], [1, 1], [1, 2], [1, 3], [2, 2], [2, 3], [3, 3]
            ])
        t[M]
            tensor([[4, 4],
                    [4, 5],
                    [4, 6],
                    [5, 5],
                    [5, 6],
                    [5, 7],
                    [6, 6],
                    [6, 7],
                    [7, 7]])


    :param tensorLen: Length of 1D tensor from you want to get spans.
    :type tensorLen: int
    :param maxSpanSize: Max size of a span.
    :type maxSpanSize: int
    :return: Mask that determines spans.
    :rtype: torch.tensor
    """
    assert tensorLen > 0
    assert maxSpanSize > 0

    res = []

    for spanStart in range(tensorLen):
        for spanSize in range(
                maxSpanSize):  # spanSize 0 means actual span size 1 because of the spanEnd-spanStart semantic
            spanEnd = spanStart + spanSize
            if spanEnd >= tensorLen:
                break
            res.append([spanStart, spanEnd])

    return torch.tensor(res)


def proliferate(x: torch.Tensor, n: int) -> torch.Tensor:
    """
    Makes "copy" (shares underlying data) of every element of tensor x n times.

    Example:
        >>> x
        tensor([[1, 0],
                [0, 1]])

        >>> proliferate(x, 4)
        tensor([[1, 0],
                [1, 0],
                [1, 0],
                [1, 0],
                [0, 1],
                [0, 1],
                [0, 1],
                [0, 1]])

    :param x: Input tensor containing elements that should be used.
    :type x: torch.Tensor
    :param n: How many times you want to "copy" each element.
    :type n: int
    :return: Tensor containing all elements n times.
    :rtype: torch.Tensor
    """
    assert n > 0

    shapeForExpand = list(x.shape)
    shapeForExpand.insert(1, n)

    shapeForReshape = list(x.shape)
    shapeForReshape[0] *= n

    """
    Step by step on example:
        X
        tensor([[1, 0],
                [0, 1]])

        X.unsqueeze(1)
        tensor([[[1, 0]],

                [[0, 1]]])

        X.unsqueeze(1).expand(shapeForExpand)
        tensor([[[1, 0],
                 [1, 0],
                 [1, 0],
                 [1, 0]],

                [[0, 1],
                 [0, 1],
                 [0, 1],
                 [0, 1]]])

        X.unsqueeze(1).expand(shapeForExpand).reshape(shapeForReshape)
        tensor([[1, 0],
                [1, 0],
                [1, 0],
                [1, 0],
                [0, 1],
                [0, 1],
                [0, 1],
                [0, 1]])
    """

    return x.unsqueeze(1).expand(shapeForExpand).reshape(shapeForReshape)

