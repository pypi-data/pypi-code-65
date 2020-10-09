# -*- coding: utf-8 -*-
import abc
from typing import Tuple, Optional

import torch
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from torch.utils.data import Dataset
from torchvision.transforms import Compose


class ObjectDetectionDataset(Dataset, metaclass=abc.ABCMeta):
    """
    Abstract Dataset class for object detection
    """

    def __init__(self, transform: Optional[Compose] = None):
        self._transform = transform

    def _open_img(self, img_path: str):
        img = Image.open(img_path)
        if self._transform:
            img = self._transform(img)
        return img

    @abc.abstractmethod
    def __getitem__(self, index: int) -> Tuple[JpegImageFile, torch.Tensor]:
        """
        Get image and labels
        Args:
            index: index of data

        Returns:
            jpg image and labels
        """
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        pass
