# -*- coding: UTF-8 -*-
""""
Created on 25.10.19
This module contains factory classes for optimizers creation.

:author:     Martin Dočekal
"""

from abc import ABC, abstractmethod
from typing import Union, Iterable, Optional

import torch


class OptimizerCreator(ABC):
    """
    Abstract base class for optimizers creation. (it's factory)
    """

    @abstractmethod
    def create(self, module: torch.nn.Module) -> torch.optim.Optimizer:
        """
        Creates optimizer for given module.

        :param module: Module which parameters you want to optimize.
        :type params: torch.nn.Module
        :return: Created optimizer for given module and with settings that are hold by creator object.
        :rtype: torch.optim.Optimizer
        """
        pass

    @abstractmethod
    def createForParams(self, params: Union[Iterable[torch.Tensor], Iterable[dict]]) -> torch.optim.Optimizer:
        """
        Creates optimizer for given parameters.

        :param params: Parameters that should be optimized.
            An iterable of torch.Tensors or dicts which specifies which Tensors should be optimized along with group
            specific optimization options.
                Example of groups:
                    [
                        {'params': ..., 'weight_decay': ...},
                        {'params': ..., 'weight_decay': ...}
                    ]
        :type params: Union[Iterable[torch.Tensor], Iterable[dict]]
        :return: Created optimizer for given params and with settings that are hold by creator object.
        :rtype: torch.optim.Optimizer
        """
        pass


class AdamWOptimizerCreator(OptimizerCreator):
    """
    Creator for AdamW (adam with weight decay) optimizer.
    """

    DEFAULT_LEARNING_RATE = 1e-6
    DEFAULT_EPSILON = 1e-8
    DEFAULT_WEIGHT_DECAY = 1e-2

    def __init__(self, learningRate: float = DEFAULT_LEARNING_RATE, epsilon: float = DEFAULT_EPSILON,
                 weightDecay: float = DEFAULT_WEIGHT_DECAY):
        """
        Initialization of creator settings.

        :param learningRate: Default learning rate. Group specific could be set in dictionary in params argument for
            create method.
        :type learningRate: float
        :param epsilon: Term added to the denominator to improve numerical stability.
            This is default epsilon. Group specific could be set in dictionary in params argument for create method.
        :type epsilon: float
        :param weightDecay: Weight decay coefficient that is used for changing of loss in this kind of way:
                Loss = Original loss + weightDecay * sum(w^2)
            Where w are model parameters. We are trying to decrease model complexity to prevent over fitting.

            This is default weight decay. Group specific could be set in dictionary in params argument for create method.
        :type weightDecay: float
        """

        self.learningRate = learningRate
        self.epsilon = epsilon
        self.weightDecay = weightDecay

    def create(self, module: torch.nn.Module) -> torch.optim.Optimizer:
        return self.createForParams(module.parameters())

    def createForParams(self, params: Union[Iterable[torch.Tensor], Iterable[dict]]) -> torch.optim.Optimizer:
        return torch.optim.AdamW(params, lr=self.learningRate, eps=self.epsilon,
                                 weight_decay=self.weightDecay)


class BERTAdamWOptimizerCreator(AdamWOptimizerCreator):
    """
    Same as AdamWOptimizerCreator, but can exclude some parameters from weight decay (by default).
    """

    def __init__(self, learningRate: float = AdamWOptimizerCreator.DEFAULT_LEARNING_RATE,
                 epsilon: float = AdamWOptimizerCreator.DEFAULT_EPSILON,
                 weightDecay: float = AdamWOptimizerCreator.DEFAULT_WEIGHT_DECAY,
                 excludeFromWeightDecay: Optional[Iterable[str]] = ('bias', 'LayerNorm.weight')):
        """
        Initialization of creator settings.

        :param learningRate: Default learning rate. Group specific could be set in dictionary in params argument for
            create method.
        :type learningRate: float
        :param epsilon: Term added to the denominator to improve numerical stability.
            This is default epsilon. Group specific could be set in dictionary in params argument for create method.
        :type epsilon: float
        :param weightDecay: Weight decay coefficient that is used for changing of loss in this kind of way:
                Loss = Original loss + weightDecay * sum(w^2)
            Where w are model parameters. We are training to decrease model complexity to prevent over fitting.
            This is default weight decay. Group specific could be set in dictionary in params argument for create method.
        :type weightDecay: float
        :param excludeFromWeightDecay: Names (substrings of name) of parameters that should be excluded from weight decay.

            By default excludes all parameters with these substrings in names:
                'bias', 'LayerNorm.weight'
            The default values should be the same as for original BERT model, but I was not able to find the reason behind that choice.
                    Same choice is used in: https://github.com/huggingface/transformers/blob/master/examples/run_squad.py#L96
                    Also probably equivalent choice is in: https://github.com/google-research/bert/blob/master/optimization.py#L65

            !!! WARNING !!! - this argument works only with create method and no with createForParams, also don't
                forget to set weightDecay argument.
        :type excludeFromWeightDecay: Optional[Iterable[str]]
        """

        self.learningRate = learningRate
        self.epsilon = epsilon
        self.weightDecay = weightDecay
        self.excludeFromWeightDecay = excludeFromWeightDecay

    def create(self, module: torch.nn.Module) -> torch.optim.Optimizer:
        if self.excludeFromWeightDecay is not None:
            groupedParameters = [
                {"params": [], "weight_decay": self.weightDecay},
                {"params": [], "weight_decay": 0.0}
            ]

            for name, params in module.named_parameters():
                if any(nameSubstringExclude in name for nameSubstringExclude in self.excludeFromWeightDecay):
                    # Exclude this parameter, because its name contains substring that determines excluded parameters.
                    groupedParameters[1]["params"].append(params)
                else:
                    groupedParameters[0]["params"].append(params)

        return self.createForParams(groupedParameters)
