# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for computing model evaluation metrics."""
import logging

import numpy as np

from typing import Any, List, Optional

from azureml.automl.runtime.shared.score import _scoring_utilities


def pad_predictions(y_pred_probs: np.ndarray,
                    train_labels: Optional[np.ndarray],
                    class_labels: Optional[np.ndarray]) -> np.ndarray:
    """This function is deprecated."""
    logging.warning("azureml.automl.runtime.shared.metrics_utilities.pad_predictions is deprecated "
                    "and will be removed in a future version of the AzureML SDK")

    return _scoring_utilities.pad_predictions(y_pred_probs, train_labels, class_labels)
