# -*- coding: UTF-8 -*-
""""
Created on 15.05.20

Module for tensor values filters.

:author:     Martin Dočekal
"""

from abc import ABC, abstractmethod

import torch
from scipy.stats import t as tDist
import math


class Filter(ABC):
    """
    Base class for functors that serves as filters for tensor values.
    """

    @abstractmethod
    def __call__(self, values: torch.Tensor) -> torch.Tensor:
        """
        Performs filtering.

        :param values: The tensor you want to filter.
        :type values: torch.Tensor
        :return: Filtered values.
        :rtype: torch.Tensor
        """
        pass

    @abstractmethod
    def argFilter(self, values: torch.Tensor) -> torch.Tensor:
        """
        Performs filtering, but in contrast with __call__ return indices of values instead.

        :param values: The tensor you want to filter.
        :type values: torch.Tensor
        :return: Indices of values.
        :rtype: torch.Tensor
        """
        pass


class GrubbssFilter(Filter):
    """
    Filters out values according to one sided Grubbs's test for outliers.
        https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h1.htm
        https://en.wikipedia.org/wiki/Grubbs%27s_test_for_outliers

    """

    FLOAT_32_MACHINE_EPSILON = 2 ** (-24)
    """
    This value is politely stolen from: https://en.wikipedia.org/wiki/Machine_epsilon .
    """

    def __init__(self, alpha: float = 0.05, outliers: bool = True, sort: bool = True, descending: bool = True):
        """
        Initialization of filter.

        :param alpha: Significance level on which group test should be performed.
        :type alpha: float
        :param outliers:
            True: Outliers are in this case considered as desirable, so they will appear on the output
            False: Outliers are filtered out.
        :type outliers: float
        :param sort:
            This filter works on sorted values. Pass true if you want that the filter will sort the values itself.
            If you want to sort the values in advance pass false. Take on mind that the sorting determines which outliers
            will be discovered (see descending comment).
        :type sort: bool
        :param descending:
            This is parameter for sorting, so it takes an effect only when sort is True.

            True: The test will be performed from the max value to the min until we will be finding outliers.
            False: Same as true, but in reversed order, from the min value to the max.
        :type descending: bool
        """

        self.alpha = alpha
        self.outliers = outliers
        self.sort = sort
        self.descending = descending

    def __call__(self, values: torch.Tensor) -> torch.Tensor:
        return values[self.argFilter(values)]

    def argFilter(self, values: torch.Tensor) -> torch.Tensor:
        # we are performing repeatedly one sided Groubbs's test.
        # Groubbs's test zero hypothesis is:
        #   H0: 	There are no outliers in the data set
        #
        if len(values.shape) != 1:
            ValueError("GrubbssFilter accepts one dimensional tensors only, but the input tensor shape is: {}.".format(values.shape))

        if self.sort:
            # assuming that the values are not sorted in advance
            values, indices = torch.sort(values, descending=self.descending)

        if self.outliers:
            res = torch.zeros(values.shape[0], dtype=torch.bool)  # reject all by default
        else:
            res = torch.ones(values.shape[0], dtype=torch.bool)  # accept all by default

        for i in range(values.shape[0]):
            actSample = values[i:]
            diffFromMean = abs(actSample[0].item() - torch.mean(actSample).item())
            std = torch.std(actSample).item()

            if abs(diffFromMean - 0) < actSample.shape[0] * self.FLOAT_32_MACHINE_EPSILON:
                # just for better numerical stability, because the actSample is expected to be long
                # Because for
                #   actSample torch.shape([130816]) [tensor([32.0024, 32.0024, 32.0024,  ..., 32.0024, 32.0024, 32.0024])]
                #  you can get:
                #   G = 178.5738
                #  Because
                #   torch.mean(actSample) tensor(32.0021)   # not 32.0024 probably because we have large summation
                #   torch.std(actSample) tensor(1.9226e-06)
                #  and the difference with the mean is not unfortunately zero
                #  so for this small std you get such a big number.
                #
                # Why the multiplication with the sample length? because we are assuming error in the summation.
                # and according to (https://www.reidatcheson.com/statistics/floating%20point/error/2018/01/15/float-sum-errors.html)
                # the worst case relative error can be calculated in that way.
                G = 0
            else:
                G = diffFromMean / std

            N = actSample.shape[0]

            # critical value of the t distribution (significance level self.alfa/N, N-2 degrees of freedom)
            t = tDist.ppf(1 - self.alpha / N, N - 2)
            t *= t

            criticalValueForTest = ((N - 1) / math.sqrt(N)) * math.sqrt(t / (N - 2 + t))

            #   0 tensor(True) tensor(123.4259) 4.94401397733683 130816 24.447842412797193
            if G > criticalValueForTest:
                # we are rejecting the zero hypothesis which means that we have an outlier
                res[i] = ~res[i]
            else:
                break

        if self.sort:
            return indices[res]
        else:
            return res.nonzero().flatten()
