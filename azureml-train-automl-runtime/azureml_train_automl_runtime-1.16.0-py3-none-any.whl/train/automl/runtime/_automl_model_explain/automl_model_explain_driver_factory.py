# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Any, Dict
import logging

from azureml.core import Run
from azureml.automl.runtime.shared.datasets import DatasetBase
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentWithSupportedValues
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_classification_driver import \
    AutoMLModelExplainClassificationDriver
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_forecasting_driver import \
    AutoMLModelExplainForecastingDriver
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_regression_driver import \
    AutoMLModelExplainRegressionDriver
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_streaming_driver import \
    AutoMLModelExplainStreamingDriver
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_driver import \
    AutoMLModelExplainDriver
from azureml._common._error_definition import AzureMLError


logger = logging.getLogger(__name__)


class AutoMLModelExplainDriverFactory:

    @staticmethod
    def _get_model_explain_driver(
            automl_child_run: Run, dataset: DatasetBase,
            automl_settings: AutoMLBaseSettings,
            model_exp_workspace_config: Optional[Dict[str, Any]] = None) -> AutoMLModelExplainDriver:
        """
        Get the model explain configuration class for a given type of AutoMl model.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param dataset: Containing X, y and other transformed data info.
        :type dataset: DatasetBase
        :param automl_settings: Automated ML run settings.
        :type automl_settings: AutoMLBaseSettings
        :param model_exp_feature_config: Model explainability configuration.
        :type model_exp_feature_config: Dict
        :return: Configuration class for explaining a given AutoML model.
        """
        if automl_settings.enable_streaming:
            logger.info("Constructing model explain config for streaming with task " + automl_settings.task_type)
            return AutoMLModelExplainStreamingDriver(
                automl_child_run=automl_child_run,
                dataset=dataset,
                max_cores_per_iteration=automl_settings.max_cores_per_iteration,
                task_type=automl_settings.task_type,
                model_exp_workspace_config=model_exp_workspace_config)
        elif automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            logger.info("Constructing model explain config for classification")
            return AutoMLModelExplainClassificationDriver(
                automl_child_run=automl_child_run,
                dataset=dataset,
                max_cores_per_iteration=automl_settings.max_cores_per_iteration,
                model_exp_workspace_config=model_exp_workspace_config)
        elif automl_settings.task_type == constants.Tasks.REGRESSION:
            if not automl_settings.is_timeseries:
                logger.info("Constructing model explain config for regression")
                return AutoMLModelExplainRegressionDriver(
                    automl_child_run=automl_child_run,
                    dataset=dataset,
                    max_cores_per_iteration=automl_settings.max_cores_per_iteration,
                    model_exp_workspace_config=model_exp_workspace_config)
            else:
                logger.info("Constructing model explain config for forecasting")
                return AutoMLModelExplainForecastingDriver(
                    automl_child_run=automl_child_run,
                    dataset=dataset,
                    max_cores_per_iteration=automl_settings.max_cores_per_iteration,
                    model_exp_workspace_config=model_exp_workspace_config)
        else:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="task",
                    arguments="task ({})".format(automl_settings.task_type),
                    supported_values=", ".join(
                        [constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION, constants.Subtasks.FORECASTING]
                    )
                )
            )
