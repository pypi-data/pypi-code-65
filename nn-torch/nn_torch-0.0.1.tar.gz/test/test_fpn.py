# -*- coding: utf-8 -*-
from typing import List

import torch

from nn_torch.cv.fpn import FPN
from nn_torch.cv.fpnbody import ResNet34FPNBody, MobileNetV3LargeFPNBody
from nn_torch.cv.resnet import ResNet34
from nn_torch.cv.mobilenet import MobileNetV3Large


def test_fpn():
    out_channels = 256
    batch_size = 10

    fpns: List[FPN] = [FPN(ResNet34FPNBody(ResNet34()), out_channels),
                       FPN(MobileNetV3LargeFPNBody(MobileNetV3Large()), out_channels)]

    x = torch.rand([batch_size, 3, 224, 224])
    for fpn in fpns:
        features = fpn(x)
        assert len(features) == len(fpn.body.in_channels_tuple)
        last_feature_sizes = list(features[0].shape[-2:])
        for feat in features:
            assert feat.shape == torch.Size([batch_size, out_channels] + last_feature_sizes)
            last_feature_sizes[0] *= 2
            last_feature_sizes[1] *= 2
