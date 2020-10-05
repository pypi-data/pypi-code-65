""" SimCLR with ResNets """

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

import torch.nn as nn
from lightly.models._resnet import ResNetGenerator


class ResNetSimCLR(nn.Module):
    """ Self-supervised model with ResNet architecture

    """

    def __init__(self, name='resnet-18', width=1, num_ftrs=16, out_dim=128):
        """ Constructor

        Args:
            name: (str) ResNet version from resnet-{9, 18, 34, 50, 101, 152}
            num_ftrs: (int) Embedding dimension
            out_dim: (int) Output dimension

        """

        self.num_ftrs = num_ftrs
        self.out_dim = out_dim

        super(ResNetSimCLR, self).__init__()
        resnet = ResNetGenerator(name=name, width=width)

        last_conv_channels = list(resnet.children())[-1].in_features

        self.features = nn.Sequential(
            nn.BatchNorm2d(3),
            *list(resnet.children())[:-1],
            nn.Conv2d(last_conv_channels, num_ftrs, 1),
            nn.AdaptiveAvgPool2d(1)
        )

        self.projection_head = nn.Sequential(
            nn.Linear(num_ftrs, num_ftrs),
            nn.ReLU(),
            nn.Linear(num_ftrs, out_dim)
        )

    def forward(self, x):
        """ Forward pass through ResNetSimCLR

        Args:
            x: (tensor) bsz x channels x W x H

        Returns:
            embeddings: (tensor) bsz x n_features
        """
        # embed images in feature space
        emb = self.features(x)
        emb = emb.squeeze()

        # return projection to space for loss calcs
        return self.projection_head(emb)
