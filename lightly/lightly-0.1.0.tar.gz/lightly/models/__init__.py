""" lightly.models

    The lightly.models module provides a collection of 
    models (such as ResNet) which can easily be used 
    for self-supervised learning.

"""

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

from lightly.models._resnet import ResNetGenerator
from lightly.models._simclr import ResNetSimCLR
from lightly.models._zoo import ZOO
