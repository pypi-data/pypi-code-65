""" lightly.data

    The lightly.data module provides a dataset wrapper
    and useful collate functions for self-supervised learning
    (see torch.utils.data.DataLoader for details on collate_fn)

"""

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

from lightly.data._dataset import LightlyDataset
from lightly.data._collate import BaseCollateFunction
from lightly.data._collate import ImageCollateFunction
from lightly.data._utils import check_images
