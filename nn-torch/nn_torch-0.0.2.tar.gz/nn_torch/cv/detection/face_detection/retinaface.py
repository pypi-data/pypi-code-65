# -*- coding: utf-8 -*-
from math import ceil
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from mmcv.ops import DeformConv2dPack

from nn_torch.cv.detection.fpn import FPN


class ContextModule(nn.Module):
    """
    Applied context modules on feature pyramids to
    enlarge the receptive field from Euclidean grids
    """

    def __init__(self, in_channels: int, out_channels: int, device: torch.device):
        super().__init__()
        assert out_channels % 4 == 0

        build_conv_func = self.__build_dcn if device.type == 'cuda' else self.__build_conv

        self.conv1 = build_conv_func(in_channels, out_channels // 2)
        self.conv2 = build_conv_func(out_channels // 2, out_channels // 4)
        self.conv3 = build_conv_func(out_channels // 4, out_channels // 4)

    @staticmethod
    def __build_dcn(in_channels: int, out_channels: int):
        return nn.Sequential(
            DeformConv2dPack(in_channels=in_channels,
                             out_channels=out_channels,
                             kernel_size=3,
                             padding=1,
                             bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    @staticmethod
    def __build_conv(in_channels: int, out_channels: int):
        return nn.Sequential(
            nn.Conv2d(in_channels,
                      out_channels,
                      kernel_size=3,
                      padding=2,
                      dilation=2,
                      bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor):
        out1 = self.conv1(x)
        out2 = self.conv2(out1)
        out3 = self.conv3(out2)

        return torch.cat((out1, out2, out3), dim=1)


class ClassHead(nn.Module):
    """
    Args:
        cls_num: 分类个数
    """

    def __init__(self, in_channels: int, cls_num: int, anchor_num_per_grid: int):
        super(ClassHead, self).__init__()
        self.conv1x1 = nn.Conv2d(in_channels, anchor_num_per_grid * cls_num, kernel_size=(1, 1))

    def forward(self, x):
        out = self.conv1x1(x)
        out = out.permute(0, 2, 3, 1).contiguous()

        return out.view(out.shape[0], -1, 2)


class BboxHead(nn.Module):
    """
    回归bound box
    """

    def __init__(self, in_channels: int, anchor_num_per_grid: int):
        super(BboxHead, self).__init__()

        # 中心点偏移量坐标 + 锚框长宽
        self.conv1x1 = nn.Conv2d(in_channels, anchor_num_per_grid * 4, kernel_size=1)

    def forward(self, x):
        out = self.conv1x1(x)
        out = out.permute(0, 2, 3, 1).contiguous()

        return out.view(out.shape[0], -1, 4)


class LandmarkHead(nn.Module):
    """
    人脸关键点回归
    """

    def __init__(self, in_channels, anchor_num_per_grid):
        super(LandmarkHead, self).__init__()

        # 5个关键点, 每个关键点2个坐标
        self.conv1x1 = nn.Conv2d(in_channels, anchor_num_per_grid * 10, kernel_size=(1, 1))

    def forward(self, x):
        out = self.conv1x1(x)
        out = out.permute(0, 2, 3, 1).contiguous()

        return out.view(out.shape[0], -1, 10)


class RetinaFace(nn.Module):

    def __init__(self, fpn: FPN, cls_num: int, anchor_num_per_grid: int, device: torch.device):
        super().__init__()
        self.fpn = fpn
        out_channels = self.fpn.out_channels
        self.cxt_modules = nn.ModuleList(
            [ContextModule(out_channels, out_channels, device) for _ in range(fpn.features_num)])

        self.class_heads = nn.ModuleList(
            [ClassHead(out_channels, cls_num, anchor_num_per_grid) for _ in range(fpn.features_num)])
        self.bbox_heads = nn.ModuleList([BboxHead(out_channels, anchor_num_per_grid) for _ in range(fpn.features_num)])
        self.landmark_heads = nn.ModuleList(
            [LandmarkHead(out_channels, anchor_num_per_grid) for _ in range(fpn.features_num)])

    def forward(self, x: torch.Tensor):
        features = self.fpn(x)
        features = [cxt_module(feat) for cxt_module, feat in zip(self.cxt_modules, features)]

        bbox_regs = torch.cat([bbox_head(feat) for bbox_head, feat in zip(self.bbox_heads, features)], dim=1)
        clsfs = torch.cat([cls_head(feat) for cls_head, feat in zip(self.class_heads, features)], dim=1)
        ldm_regs = torch.cat([ldm_head(feat) for ldm_head, feat in zip(self.landmark_heads, features)], dim=1)

        return bbox_regs, (clsfs if self.training else F.softmax(clsfs, dim=-1)), ldm_regs


class RetinaFaceAnchorGenerator:
    """
    深的层用于检测大物体，浅的层用于检测小物体
    """

    def __init__(self, *,
                 scale_step: float,
                 strides: List[int],
                 img_size: int):
        self.scale_step = scale_step
        self.strides = strides
        self.img_size = img_size
        self.feat_sizes = [[ceil(self.img_size / stride)] * 2 for stride in
                           self.strides]

    @property
    def anchor_nums(self):
        return [len(range(0, self.img_size, stride)) ** 2 * 3 for stride in self.strides]

    def gen_anchors(self) -> torch.Tensor:
        anchors = []

        for stride in self.strides:
            h = w = stride * 4
            for x_min in range(0, self.img_size, stride):
                for y_min in range(0, self.img_size, stride):
                    # 正方形 y_min = x_min
                    x_c = x_min + stride / 2
                    y_c = y_min + stride / 2
                    anchors.extend((x_c, y_c, w, h,
                                    x_c, y_c, w * self.scale_step, h * self.scale_step,
                                    x_c, y_c, w * self.scale_step ** 2, h * self.scale_step ** 2))
        output = torch.Tensor(anchors).view(-1, 4)
        return output


def decode_bbox(bbox_delta: torch.Tensor, anchors: torch.Tensor, variances: Tuple[float, float]) -> torch.Tensor:
    boxes = torch.cat((anchors[:, :2] + bbox_delta[:, :, :2] * variances[0] * anchors[:, 2:],
                       anchors[:, 2:] * torch.exp(bbox_delta[:, :, 2:] * variances[1])), dim=2)
    boxes[:, :, :2] -= boxes[:, :, 2:] / 2
    boxes[:, :, 2:] += boxes[:, :, :2]
    return boxes


def decode_landmark(ldm, anchors, variance: float):
    """关键点解码"""
    return torch.cat((anchors[:, :2] + ldm[:, :, :2] * variance * anchors[:, 2:],
                      anchors[:, :2] + ldm[:, :, 2:4] * variance * anchors[:, 2:],
                      anchors[:, :2] + ldm[:, :, 4:6] * variance * anchors[:, 2:],
                      anchors[:, :2] + ldm[:, :, 6:8] * variance * anchors[:, 2:],
                      anchors[:, :2] + ldm[:, :, 8:10] * variance * anchors[:, 2:],
                      ), dim=2)
