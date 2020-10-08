# -*- coding: utf-8 -*-
import abc
from typing import Tuple

import torch
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from torch.utils.data import Dataset


class RetinaFaceDataset(Dataset, metaclass=abc.ABCMeta):

    def __init__(self, transform=None):
        self._transform = transform

    def _open_img(self, img_path: str):
        img = Image.open(img_path)
        if self._transform:
            img = self._transform(img)
        return img

    @abc.abstractmethod
    def __getitem__(self, index: int) -> Tuple[JpegImageFile, torch.Tensor]:
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass
