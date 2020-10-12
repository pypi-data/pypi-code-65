import numpy as np
import pandas as pd

from disaster_messaging_classification_model.utils.model_utils import load_pipeline
from disaster_messaging_classification_model.config import config

from disaster_messaging_classification_model import __version__ as _version

import logging
import typing as t

_logger = logging.getLogger(__name__)

pipeline_file_name = f"{config.MODEL_SAVE_FILE}{_version}.pkl"
model_pipeline = load_pipeline(file_name=pipeline_file_name)


def make_prediction(*, input_data: t.Union[pd.Series, dict]) -> dict:
    """Make a prediction using a saved model pipeline.

    Args:
        input_data: Array of model prediction inputs.

    Returns:
        Predictions for each input row, as well as the model version.
    """

    data = pd.Series(input_data)

    prediction_array = model_pipeline.predict(data)

    # convert predictions to a json record response
    predictions_df = pd.DataFrame(data=prediction_array, columns=config.CLASSES)
    predictions = predictions_df.to_dict(orient="records")

    response = {"predictions": predictions, "version": _version}

    _logger.info(
        f"Making predictions with model version: {_version} "
        f"Inputs: {data} "
        f"Predictions: {response}"
    )

    return response
