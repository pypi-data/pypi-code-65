from typing import Callable, Optional, Protocol, Union
from torch import nn
import tensorflow.keras as tfk
import torch
from torch.utils.data.dataloader import DataLoader
from torch.optim.optimizer import Optimizer


class Trainable(Protocol):
    model: nn.Module

    def train(self, epochs: int, train_dataloader: DataLoader,
              valid_dataloader: DataLoader, valid_interval: int,
              test_dataloader: DataLoader, test_interval: int,
              **kwargs):
        """
        Training
        """
        for e in range(1, epochs):
            self.train_one_epoch(epoch=e, dataloader=train_dataloader, **kwargs)
            if e % valid_interval == 0:
                self.valid(dataloader=valid_dataloader)
            if e % test_interval == 0:
                self.test(dataloader=test_dataloader)

    def train_one_epoch(self, epoch: int, dataloader: DataLoader, **kwargs):
        raise NotImplementedError

    def valid(self, dataloader: DataLoader, **kwargs):
        """Validation"""
        raise NotImplementedError

    def test(self, dataloader: DataLoader, **kwargs):
        """Validation"""
        raise NotImplementedError

    def log(self, content: dict, prefix: str = None):
        if self.model is None:
            return
        if prefix is None:
            output = ""
        else:
            output = prefix + " |"
        for k, v in content.items():
            if isinstance(v, float):
                output = output + f"{k}: {v:.3f}" + ' | '
            else:
                output = output + f"{k}: {v}" + " | "
        output = output.strip()[:-1]
        print(output)

    def save(self, **kwargs):
        """
        Save model API
        """
        raise NotImplementedError

    def assertion(self):
        assert self.model is not None, f"Model is None."
