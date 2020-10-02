# -*- coding: UTF-8 -*-
""""
Created on 08.04.20
Module with PyTorch samplers.

:author:     Martin Dočekal
"""
import math
from typing import List

import torch
from torch.utils.data import Sampler, Dataset


class ResumableSampler(Sampler):
    """
    Random sampler that can be resumed.

    :ivar actPerm: Actually used permutation (walk trough dataset) for actual iteration.
    :vartype actPerm: Optional[List[int]]
    """

    def __init__(self, source: Dataset, shuffle: bool = False):
        """
        Initialization of resumable sampler.

        :param source: The source dataset that should be used.
        :type source: Dataset
        :param shuffle: Determines whether the dataset should be iterated in random order.
        :type shuffle: bool
        """

        self._source = source
        self._shuffle = shuffle

        self._resume = None

        self.actPerm = None

    def resume(self, perm: List[int], skip: int):
        """
        Next call of __iter__ resumes permutation and skips first skip samples from beginning of this
        permutation. All the other future __iter__ calls will act normal.

        :param perm: Permutation (walk trough dataset samples).
        :type perm: List[int]
        :param skip: Number of samples from beginning (according to order derived from loaded permutation) that should
            be skipped.
        :type skip: int
        """

        self._resume = (perm, skip)

    def __iter__(self):
        if self._resume is None:
            self.actPerm = torch.randperm(len(self)).tolist() if self._shuffle else torch.arange(len(self)).tolist()
        else:
            # we want to restore saved permutation
            self.actPerm = self._resume[0][self._resume[1]:]
            self._resume = None

        for idx in self.actPerm:
            yield idx

    def __len__(self):
        return len(self._source)


class IndicesSubsampler(Sampler):
    """
    Sample for subsampling.
        https://en.wikipedia.org/wiki/Resampling_(statistics)#Subsampling

    These sampler does not provides the data itself, but just the indices that should be selected.
    """

    def __init__(self, source: Dataset, subsetLen: int):
        """
        Len of subsampled dataset.

        :param source: Source dataset you want to sample from. We need it just for the len.
        :type source: Dataset
        :param subsetLen: Len of dataset after subsampling.
        :type subsetLen: int
        """
        assert subsetLen <= len(source)

        self.source = source
        self.subsetLen = subsetLen

    def __len__(self):
        return self.subsetLen

    def __iter__(self):
        for x in torch.randperm(len(self.source))[:self.subsetLen]:
            yield int(x)


class SlidingBatchSampler(Sampler):
    """
    Wraps another sampler to yield a mini-batch of indices.
    In sliding window fashion.

    """

    def __init__(self, sampler: Sampler, batchSize: int, stride: int, dropLast: bool):
        """
        Initialization of sampler.

        :param sampler: Sampler that provides indices for a batch.
        :type sampler: Sampler
        :param batchSize: Size of a single batch.
        :type batchSize: int
        :param stride: Shift between two batches.
        :type stride: int
        :param dropLast: If true than drops the last batch that will not have whole size.
        :type dropLast: bool
        """
        if not isinstance(sampler, Sampler):
            raise ValueError("sampler should be an instance of "
                             "torch.utils.data.Sampler, but got sampler={}"
                             .format(sampler))
        if not isinstance(batchSize, int) or isinstance(batchSize, bool) or \
                batchSize <= 0:
            raise ValueError("batchSize should be a positive integer value, "
                             "but got batchSize={}".format(batchSize))

        if not isinstance(stride, int) or isinstance(stride, bool) or \
                stride <= 0:
            raise ValueError("stride should be a positive integer value, "
                             "but got stride={}".format(stride))

        if not isinstance(dropLast, bool):
            raise ValueError("dropLast should be a boolean value, but got "
                             "dropLast={}".format(dropLast))

        self.sampler = sampler
        self.batchSize = batchSize
        self.stride = stride
        self.dropLast = dropLast

    def __iter__(self):
        batch = []
        notFlushed = False
        skip = 0
        for idx in self.sampler:
            if skip > 0:
                skip -= 1
                continue
            batch.append(idx)
            notFlushed = True
            if len(batch) == self.batchSize:
                notFlushed = False
                yield batch
                batch = batch[self.stride:]

                if self.stride > self.batchSize:
                    skip = self.stride - self.batchSize

        if not self.dropLast and notFlushed:
            yield batch

    def __len__(self):
        if len(self.sampler) == 0:
            return 0
        elif len(self.sampler) < self.batchSize:
            return 0 if self.dropLast else 1
        else:
            # Derivation of formula:
            # We are finding number of slide window steps when the window end would reach the end of data set of length L (len(self.sampler)).
            #   window_end(step) = L
            #
            #   window_end(step) is function that returns offset of window end on given step (for now step can be non integer number)
            #       window_end(step) = (step - 1)*stride + batchSize
            #
            #   (step - 1)*stride + batchSize = L
            #                      (step - 1) = (L - batchSize) / stride
            #                            step = 1 + (L - batchSize) / stride
            #
            #   The step is almost result of out __len__ method, but we need positive integer. So we will use ceil or floor
            #   depending on the drop_last and also the min to get positive number.

            step = 1 + (len(self.sampler) - self.batchSize) / self.stride

            if self.dropLast:
                return math.floor(step)
            else:
                return math.ceil(step)
