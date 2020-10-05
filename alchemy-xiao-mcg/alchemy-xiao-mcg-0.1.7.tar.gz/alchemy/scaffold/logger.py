# Logger classes.
# This file import supported loggers (WandB and Tensorboard are supported now)
# and adding some dirty hack to make Wandb works with DDP
# Reference and adapted from:
#  https://github.com/PyTorchLightning/pytorch-lightning/issues/981
# Author: Xiao Li

from pytorch_lightning.loggers import WandbLogger, TensorBoardLogger                # noqa : F401
# A dirty hack to make WandbLogger works under DDP.
setattr(WandbLogger, 'name', property(lambda self: self._name))
