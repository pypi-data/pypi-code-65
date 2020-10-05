# -*- coding: utf-8 -*-
import abc
from typing import List

import torch
import torch.nn as nn
import torch.nn.functional as F

__all__ = ["FPN"]


class FPN(nn.Module):
    """
    FPN Module

    References: http://arxiv.org/abs/1612.03144
    """

    class FPNBody(metaclass=abc.ABCMeta):

        @property
        @abc.abstractmethod
        def in_channels_tuple(self) -> tuple:
            pass

        @abc.abstractmethod
        def bottom_up(self, x: torch.Tensor):
            pass

    def __init__(self, body: FPNBody, features_num: int = 3, out_channels: int = 256):
        super().__init__()
        self._features_num = features_num
        self.body = body

        self.inner_block_modules = [nn.Conv2d(kernel_size=1, in_channels=i, out_channels=out_channels) for i in
                                    body.in_channels_tuple]
        self.layer_block_modules = [
            nn.Conv2d(kernel_size=3, in_channels=out_channels, out_channels=out_channels, padding=1) for _ in
            range(len(body.in_channels_tuple))]

    def forward(self, x: torch.Tensor) -> List[torch.Tensor]:
        layers = self.body.bottom_up(x)

        last_layer = self.inner_block_modules[0](layers[0])
        features = [self.layer_block_modules[0](last_layer)]

        feat_shape = list(layers[1].shape[-2:])
        for idx, layer in enumerate(layers[1:], start=1):
            up_sample = F.interpolate(last_layer, size=feat_shape)

            # undergoes a 1x1 convolutional layer to reduce channel dimensions
            inner_layer = self.inner_block_modules[idx](layer)
            last_layer = inner_layer + up_sample
            feat = self.layer_block_modules[idx](last_layer)
            features.append(feat)
            feat_shape[0] *= 2
            feat_shape[1] *= 2

        return features
