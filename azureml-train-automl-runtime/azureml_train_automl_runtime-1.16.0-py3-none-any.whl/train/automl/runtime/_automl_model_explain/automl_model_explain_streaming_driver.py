# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Any, Dict, cast
import logging

from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_driver import AutoMLModelExplainDriver
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_helper import \
    _automl_auto_mode_get_explainer_data_streaming, _automl_pick_evaluation_samples_explanations
from azureml.train.automl.runtime.automl_explain_utilities import _get_unique_classes, _get_estimator_streaming
from azureml.automl.runtime.streaming_pipeline_wrapper import StreamingPipelineWrapper
from azureml.core import Run
from azureml.automl.runtime.shared.datasets import DatasetBase
from azureml.automl.core.shared import constants


logger = logging.getLogger(__name__)


class AutoMLModelExplainStreamingDriver(AutoMLModelExplainDriver):
    def __init__(self, automl_child_run: Run, dataset: DatasetBase,
                 max_cores_per_iteration: int, task_type: str,
                 model_exp_workspace_config: Optional[Dict[str, Any]] = None):
        """
        Class for model explain configuration for AutoML streaming models.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param dataset: Containing X, y and other transformed data info.
        :type dataset: DatasetBase
        :param max_cores_per_iteration: Number of cores configuration used for AutoML models.
        :type max_cores_per_iteration: int
        :param model_exp_feature_config: Model explainability configuration.
        :type model_exp_feature_config: Dict
        :param task_type: 'classification'/'regression'.
        :type task_type: str
        """
        super().__init__(automl_child_run=automl_child_run, dataset=dataset,
                         max_cores_per_iteration=max_cores_per_iteration,
                         model_exp_workspace_config=model_exp_workspace_config)
        self._task_type = task_type

    def setup_model_explain_train_data(self) -> None:
        """Training/Evaluation data to explain and down-sampling if configured."""
        # Setup the training and test samples for explanations
        explainer_train_data, explainer_test_data, explainer_data_y, explainer_data_y_valid = \
            _automl_auto_mode_get_explainer_data_streaming(self._dataset)

        # Sub-sample the validation set for the explanations
        explainer_test_data = _automl_pick_evaluation_samples_explanations(
            explainer_train_data, explainer_data_y, explainer_test_data, explainer_data_y_valid,
            is_classification=(self._dataset.get_class_labels() is not None))

        self._automl_explain_config_obj._X_transform = explainer_train_data
        self._automl_explain_config_obj._X_test_transform = explainer_test_data
        self._automl_explain_config_obj._y = explainer_data_y
        logger.info("Data preparation for streaming model explanations completed.")

    def setup_estimator_pipeline(self) -> None:
        """Estimator pipeline."""
        super()._rehydrate_automl_fitted_model()
        self._automl_explain_config_obj._automl_estimator = _get_estimator_streaming(
            cast(StreamingPipelineWrapper, self._automl_explain_config_obj._automl_pipeline),
            self._task_type)

    def setup_class_labels(self) -> None:
        """Return the unique classes in y or obtain classes from inverse transform using y_transformer."""
        if self._task_type == constants.Tasks.CLASSIFICATION:
            self._automl_explain_config_obj._classes = _get_unique_classes(
                y=self._automl_explain_config_obj._y,
                automl_estimator=self._automl_explain_config_obj._automl_estimator,
                y_transformer=self._dataset.get_y_transformer())
        else:
            self._automl_explain_config_obj._classes = None
