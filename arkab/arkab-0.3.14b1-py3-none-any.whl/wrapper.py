"""
Tensor and data operations

Functions:

1. Provide datasets

2. Change list data to
"""

import tensorflow as tf
import torch as th
from typing import Literal

BACKENDS = Literal['tf', 'tensorflow', 'torch', 'th', 'pytorch']
TFBACKEND = ['tf', 'tensorflow']
TORCHBACKEND = ['torch', 'th', 'pytorch']
REALBACKENDS = ['tf', 'th']


class TensorWrapper:
    def __init__(self, backend: BACKENDS = None, *gpu):
        if backend in TFBACKEND:
            self.wrapper = TensorflowWrapper(gpu)
            # use tensorflow gpu
        else:
            self.wrapper = TorchWrapper(gpu)

    def set_gpu(self, gpu: int):
        import os
        os.environ["CUDA_VISIBLE_DEVICES"] = f"{gpu}"


class TorchWrapper:  # torch wrapper
    # TODO: Multi GPU support
    def __init__(self, *gpu):
        self.gpu_enable = len(gpu) > 0
        if self.gpu_enable:
            assert len(gpu) == 1, "Multi GPU Support is not available yet"
            assert th.cuda.is_available(), "[ERR] GPU is not support in this device"
            self.device = th.device('cuda')
        else:
            self.device = th.device('cpu')

    def tensor(self, array: list):
        return th.tensor(array, dtype=th.float, device=self.device)

    def variable(self, array: list):
        return th.tensor(array, dtype=th.float, device=self.device, requires_grad=True)


# Tensorflow operations
class TensorflowWrapper:
    # TODO: Multi GPU support
    def __init__(self, *gpu):
        self.gpu_enable = len(gpu) > 0
        if self.gpu_enable:
            assert len(gpu) == 1, "Multi GPU Support is not available yet"
            self.device = '/CPU:0'
        else:
            self.device = f"/GPU:{gpu[0]}"
