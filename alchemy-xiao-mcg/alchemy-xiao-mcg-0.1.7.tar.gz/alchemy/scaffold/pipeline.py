# Base Pipeline class.
# Based on Pytorch-lightning for abstract research code from engineering code.
# Added several more features.
# For each project, inherit this and implement corrsponding research flow.
# Reference and adapted from:
#  https://pytorch-lightning.readthedocs.io/en/latest/lightning-module.html
# Author: Xiao Li

import pytorch_lightning as pl


class BasePipeline(pl.LightningModule):
    r"""
    A BasePipeline class.
    Essentially it is a lightmodule with serveral pre-defined
    common functions.
    """

    def __init__(self):
        super(BasePipeline, self).__init__()

    def forward(self):
        # Override in inherited class.
        # In most cases the Pipeline is only used for training, so forward() will not be called.
        # If you plan to directly use the Pipeline as a nn.Module for inference,
        # Then override this in your class.
        pass
