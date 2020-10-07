# -*- coding: utf-8 -*-
import torch

from nn_torch.cv.detection.mobilenet import MobileNetV3Large

from nn_torch.cv.detection.face_detection.retinaface import ContextModule, RetinaFace, BboxHead, \
    RetinaFaceAnchorGenerator, decode_bbox, decode_landmark
from nn_torch.cv.detection.fpn import FPN
from nn_torch.cv.detection.fpnbody import MobileNetV3LargeFPNBody

strides = [2, 4, 8, 16, 32]
img_size = 224
anchor_generator = RetinaFaceAnchorGenerator(
    scale_step=2 ** (1 / 3),
    strides=strides,
    img_size=img_size
)

fpn = FPN(MobileNetV3LargeFPNBody(MobileNetV3Large(4)), features_num=5, out_channels=256)


def test_context_module():
    x = torch.rand(10, 256, 56, 56)
    context_module = ContextModule(256, 256, torch.device('cpu'))
    out = context_module(x)
    assert out.shape == x.shape

    if torch.cuda.is_available():
        context_module = ContextModule(256, 256, torch.device('cuda')).cuda()
        x = torch.rand(10, 256, 56, 56).to('cuda')
        out = context_module(x)
        assert out.shape == x.shape


def test_retina_face():
    device = torch.device(
        'cuda' if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory > 2 ** 35 else 'cpu')
    net = RetinaFace(fpn, 4, 3, device).to(device)
    y = net(torch.rand(10, 3, 224, 224).to(device))
    bbox_regs, clsfs, ldm_regs = y
    del net
    anchors = anchor_generator.gen_anchors()

    assert bbox_regs.shape[1] == sum(anchor_generator.anchor_nums)
    bbox = decode_bbox(bbox_regs, anchors, (0.1, 0.2))
    assert bbox.shape[1:] == anchors.shape
    assert bbox.shape[0] == 10
    ldm = decode_landmark(ldm_regs, anchors, 0.1)
    assert ldm.shape == ldm_regs.shape


def test_retina_face_anchor_generator():
    anchors = anchor_generator.gen_anchors()
    assert anchors.shape[1] == 4
    assert anchors.shape[0] == sum(map(lambda x: (img_size // x) ** 2, strides)) * 3
    assert sum(anchor_generator.anchor_nums) == anchors.shape[0]


def test_bbox_head():
    features = fpn(torch.rand([10, 3, 224, 224]))
    anchor_num_sum = 0
    for feat in features:
        bbox_head = BboxHead(fpn.out_channels, 3)
        anchor_num_sum += bbox_head(feat).shape[1]

    assert anchor_num_sum == sum(anchor_generator.anchor_nums)
