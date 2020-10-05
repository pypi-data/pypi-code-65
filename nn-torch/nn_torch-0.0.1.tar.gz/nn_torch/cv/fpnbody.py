# -*- coding: utf-8 -*-
import torch

from nn_torch.cv.fpn import FPN
from nn_torch.cv.mobilenet import MobileNetV3Large
from nn_torch.cv.resnet import ResNet34


class ResNet34FPNBody(FPN.FPNBody):

    def __init__(self, resnet34: ResNet34):
        self._resnet34 = resnet34

    @property
    def in_channels_tuple(self) -> tuple:
        return 512, 256, 128, 64

    def bottom_up(self, x: torch.Tensor) -> tuple:
        x = self._resnet34.conv1(x)

        layer1: torch.Tensor = self._resnet34.conv2_x(x)
        layer2: torch.Tensor = self._resnet34.conv3_x(layer1)
        layer3: torch.Tensor = self._resnet34.conv4_x(layer2)
        layer4: torch.Tensor = self._resnet34.conv5_x(layer3)
        return layer4, layer3, layer2, layer1


class MobileNetV3LargeFPNBody(FPN.FPNBody):

    def __init__(self, mobilenet_v3: MobileNetV3Large):
        self._mobilenet_v3 = mobilenet_v3

    @property
    def in_channels_tuple(self) -> tuple:
        return 960, 80, 40, 24, 16

    def bottom_up(self, x: torch.Tensor) -> tuple:
        layer1: torch.Tensor = self._mobilenet_v3.conv1(x)
        layer2: torch.Tensor = self._mobilenet_v3.bneck1(layer1)
        layer3: torch.Tensor = self._mobilenet_v3.bneck2(layer2)
        layer4: torch.Tensor = self._mobilenet_v3.bneck3(layer3)
        layer5: torch.Tensor = self._mobilenet_v3.conv2(self._mobilenet_v3.bneck4(layer4))
        return layer5, layer4, layer3, layer2, layer1
