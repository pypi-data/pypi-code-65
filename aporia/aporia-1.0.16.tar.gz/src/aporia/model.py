from datetime import datetime
import logging
from typing import Any, cast, Dict, Iterable, List, Optional, Union

import aporia
from aporia.api.log_json import log_json
from aporia.api.log_predict import (
    generate_aporia_ids,
    is_valid_predict_input,
    log_predict_batch,
)
from aporia.api.log_actual import is_valid_log_actual_input, report_actual_batch
from aporia.api.model_setup import (
    add_extra_inputs,
    add_extra_outputs,
    check_model_exists,
    set_features,
)
from aporia.api.utils import (
    convert_iterable_to_list_of_specified_types,
    convert_list_members_to_lists,
    convert_scalar_to_iterable,
    convert_to_list,
)
from aporia.consts import LOGGER_NAME
from aporia.errors import AporiaError, handle_error
from aporia.event_loop import EventLoop
from aporia.graphql_client import GraphQLClient

logger = logging.getLogger(LOGGER_NAME)
FeatureValue = Union[float, int, bool, str]
PredictionIdentifier = Union[int, str]


class BaseModel:
    """Base class for Model objects."""

    def __init__(
        self,
        model_id: str,
        model_version: str,
        environment: Optional[str],
        graphql_client: Optional[GraphQLClient],
        event_loop: Optional[EventLoop],
        debug: bool,
        throw_errors: bool,
        timeout: Optional[int],
    ):
        """Initializes a BaseModel object.

        Args:
            model_id (str): Model identifier
            model_version (str): Model version
            environment (str): Environment's name
            graphql_client (Optional[GraphQLClient]): GraphQL client
            event_loop (Optional[EventLoop]): AsyncIO event loop
            debug (bool): True to enable debug mode
            throw_errors (bool): True to raise exceptions in object creation and set_features
            timeout (Optional[int]): Timeout, in seconds, for synchronous functions
        """
        logger.debug(
            "Initializing model object for model {} version {}".format(model_id, model_version)
        )
        self.model_id = model_id
        self.model_version = model_version
        self._environment = cast(str, environment)
        self._graphql_client = cast(GraphQLClient, graphql_client)
        self._event_loop = cast(EventLoop, event_loop)
        self._debug = debug
        self._throw_errors = throw_errors
        self._model_ready = False
        self._model_version_exists = False
        self._timeout = cast(int, timeout)

        # Check model existence
        if event_loop is not None and graphql_client is not None:
            self._check_model_existence()

        if not self._model_ready:
            logger.error("Model object initialization failed - model operations will not work.")

    def _check_model_existence(self):
        logger.debug(
            "Checking if model {} version {} already exists.".format(
                self.model_id, self.model_version
            )
        )
        try:
            model_exists, model_version_exists = self._event_loop.run_coroutine(
                check_model_exists(
                    graphql_client=self._graphql_client,
                    model_id=self.model_id,
                    model_version=self.model_version,
                    timeout=self._timeout,
                )
            )

            if not model_exists:
                raise AporiaError("Model {} does not exist.".format(self.model_id))

            self._model_version_exists = model_version_exists
            self._model_ready = True

        except Exception as err:
            handle_error(
                message="Creating model object failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=self._throw_errors,
                original_exception=err,
            )

    def set_features(
        self,
        feature_names: Iterable[str],
        categorical: Optional[Iterable[Union[int, str]]] = None,
    ):
        """Sets feature names and categorical features for the model.

        Args:
            feature_names (Iterable[str]): List of feature names
            categorical (Iterable[Union[int, str]], optional): A list indicating which of the
                features in the 'feature_names' argument are considered categorical.
        """
        if not self._model_ready:
            return

        logger.debug("Setting model features.")
        try:
            feature_names = convert_iterable_to_list_of_specified_types(
                iterable=feature_names, name="feature_names", types=str
            )
            if categorical is not None:
                categorical = convert_iterable_to_list_of_specified_types(
                    iterable=categorical, name="categorical", types=(str, int)
                )

            self._event_loop.run_coroutine(
                set_features(
                    graphql_client=self._graphql_client,
                    model_id=self.model_id,
                    model_version=self.model_version,
                    feature_names=feature_names,
                    categorical_features=categorical,
                    timeout=self._timeout,
                )
            )

            # If the query didn't fail, then the model version should now exist in the DB
            self._model_version_exists = True
        except Exception as err:
            handle_error(
                message="Setting features for {} failed, error: {}".format(self.model_id, str(err)),
                add_trace=self._debug,
                raise_exception=self._throw_errors,
                original_exception=err,
            )

    def add_extra_inputs(self, extra_inputs: Dict[str, str]):
        """Adds extra inputs to the model, which can then be reported in log_predict.

        Args:
            extra_inputs (Dict[str, str]): A mapping of input_name: input_type. type must
                be one of the following: 'numeric', 'categorical', 'boolean', 'string'.
        """
        if not self._model_ready:
            return

        logger.debug("Adding extra inputs")
        try:
            self._event_loop.run_coroutine(
                add_extra_inputs(
                    graphql_client=self._graphql_client,
                    model_id=self.model_id,
                    model_version=self.model_version,
                    extra_inputs=extra_inputs,
                    timeout=self._timeout,
                )
            )
        except Exception as err:
            handle_error(
                message="Adding extra inputs failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=self._throw_errors,
                original_exception=err,
            )

    def add_extra_outputs(self, extra_outputs: Dict[str, str]):
        """Adds extra outputs to the model, which can then be reported in log_predict.

        Args:
            extra_outputs (Dict[str, str]): A mapping of output_name: output_type. type
                must be one of the following: 'numeric', 'categorical', 'boolean', 'string'.
        """
        if not self._model_ready:
            return

        logger.debug("Adding extra outputs")
        try:
            self._event_loop.run_coroutine(
                add_extra_outputs(
                    graphql_client=self._graphql_client,
                    model_id=self.model_id,
                    model_version=self.model_version,
                    extra_outputs=extra_outputs,
                    timeout=self._timeout,
                )
            )
        except Exception as err:
            handle_error(
                message="Adding extra outputs failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=self._throw_errors,
                original_exception=err,
            )

    def log_predict(
        self,
        x: List[FeatureValue],
        y: Union[float, List[float]],
        confidence: Optional[Union[float, List[float]]] = None,
        occurred_at: Optional[datetime] = None,
        extra_inputs: Optional[Dict[str, FeatureValue]] = None,
        extra_outputs: Optional[Dict[str, FeatureValue]] = None,
        id: Optional[PredictionIdentifier] = None,
    ) -> Optional[int]:
        """Logs a single prediction.

        Args:
            x (List[FeatureValue]): X values for all of the features in the prediction
            y (Union[float, List[float]]): Prediction result
            confidence (Union[float, List[float]], optional): Prediction confidence. Defaults
                to None.
            occurred_at (datetime, optional): Prediction timestamp. Defaults to None.
            extra_inputs (Dict[str, FeatureValue], optional): Extra inputs, each input
                value must be a single bool, int, float or string. Defaults to None.
            extra_outputs (Dict[str, FeatureValue], optional): Extra outputs, each output
                value must be a single bool, int, float or string. Defaults to None.
            id (PredictionIdentifier, optional): A unique identifier string of the prediction.
                Defaults to None.

        Returns:
            int, optional: An Aporia generated unique identifier for the prediction,
                or None if any problem occurred

        Notes:
            * The features reported in the x parameter must be set with the set_features
              method before logging predictions.
            * Extra inputs and outputs should be defined with add_extra_inputs or
              add_extra_outputsbefore they are passed to log_predict.
            * Many libraries provide a way to convert their objects to lists:
                * numpy array: Use data.tolist()
                * pandas dataframe: Use data.values.tolist()
                * scipy sparse matrix: Use data.toarray().tolist()
        """
        try:
            if confidence is not None:
                confidence = [
                    convert_to_list(convert_scalar_to_iterable(confidence))  # type: ignore
                ]

            result = self.log_predict_batch(
                x=[convert_to_list(x)],
                y=[convert_to_list(convert_scalar_to_iterable(y))],
                confidence=confidence,  # type: ignore
                occurred_at=occurred_at,
                extra_inputs=None if extra_inputs is None else [extra_inputs],
                extra_outputs=None if extra_outputs is None else [extra_outputs],
                ids=None if id is None else [id],
            )

            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], int):
                return result[0]

            return None
        except Exception as err:
            handle_error(
                message="Logging prediction failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=False,
                original_exception=err,
                log_level=logging.ERROR,
            )
            return None

    def log_predict_batch(
        self,
        x: List[List[FeatureValue]],
        y: List[List[float]],
        confidence: Optional[List[List[float]]] = None,
        occurred_at: Optional[datetime] = None,
        extra_inputs: Optional[List[Dict[str, FeatureValue]]] = None,
        extra_outputs: Optional[List[Dict[str, FeatureValue]]] = None,
        ids: Optional[List[PredictionIdentifier]] = None,
    ) -> Optional[List[int]]:
        """Logs multiple predictions.

        Args:
            x (List[List[FeatureValue]]): X values for all of the features in each of the predictions
            y (List[List[float]]): Predictions results for each prediction
            confidence (List[List[float]], optional): Confidence for each prediction. Defaults to None.
            occurred_at (datetime, optional): Timestamp for each prediction. Defaults to datetime.now().
            extra_inputs (List[Dict[str, FeatureValue]], optional): Extra inputs for each prediction, each
                element in the list should a dict mapping the input name to its value, which
                can be bool, int, float or string. Defaults to None.
            extra_outputs (List[Dict[str, FeatureValue]], optional): Extra outputs for each prediction, each
                element in the list should a dict mapping the output name to its value, which
                can be bool, int, float or string. Defaults to None.
            ids (List[PredictionIdentifier], optional): An unique identifier string for each prediction.
                Defaults to None.

        Returns:
            List[int], optional: An Aporia generated unique identifier for each prediction, or None
                if any problem occurred

        Notes:
            * The features reported in the x parameter must be set with the set_features
              method before logging predictions.
            * Extra inputs and outputs should be defined with add_extra_inputs or
              add_extra_outputsbefore they are passed to log_predict_batch.
            * Many libraries provide a way to convert their objects to lists:
                * numpy array: Use data.tolist()
                * pandas dataframe: Use data.values.tolist()
                * scipy sparse matrix: Use data.toarray().tolist()
        """
        if not self._model_ready:
            return None

        if not self._model_version_exists:
            logger.warning(
                "Logging prediction failed: features for this model version were not reported."
            )
            return None

        logger.debug("Logging {} predictions".format(len(y)))
        try:
            x = convert_list_members_to_lists(convert_to_list(x))
            y = convert_list_members_to_lists(convert_to_list(y))
            if confidence is not None:
                confidence = convert_list_members_to_lists(convert_to_list(confidence))

            if not is_valid_predict_input(
                x=x,
                y=y,
                confidence=confidence,
                extra_inputs=extra_inputs,
                extra_outputs=extra_outputs,
                ids=ids,
            ):
                logger.warning("Logging prediction failed: Invalid input.")
                return None

            aporia_ids = generate_aporia_ids(size=len(x))

            self._event_loop.run_coroutine(
                coro=self._log_predict_batch(
                    x=x,
                    y=y,
                    aporia_ids=aporia_ids,
                    confidence=confidence,
                    occurred_at=occurred_at,
                    extra_inputs=extra_inputs,
                    extra_outputs=extra_outputs,
                    ids=ids,
                ),
                await_result=False,
            )
            return aporia_ids
        except Exception as err:
            handle_error(
                message="Logging prediction batch failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=False,
                original_exception=err,
                log_level=logging.ERROR,
            )
            return None

    async def _log_predict_batch(
        self,
        x: List[List[FeatureValue]],
        y: List[List[float]],
        aporia_ids: List[int],
        confidence: Optional[List[List[float]]] = None,
        occurred_at: Optional[datetime] = None,
        extra_inputs: Optional[List[Dict[str, FeatureValue]]] = None,
        extra_outputs: Optional[List[Dict[str, FeatureValue]]] = None,
        ids: Optional[List[PredictionIdentifier]] = None,
    ):
        try:
            await log_predict_batch(
                graphql_client=self._graphql_client,
                model_id=self.model_id,
                model_version=self.model_version,
                environment=self._environment,
                x=x,
                y=y,
                aporia_ids=aporia_ids,
                confidence=confidence,
                occurred_at=occurred_at,
                extra_inputs=extra_inputs,
                extra_outputs=extra_outputs,
                user_ids=ids,
            )
        except Exception as err:
            handle_error(
                message="Logging prediction failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=False,
                original_exception=err,
                log_level=logging.ERROR,
            )

    def log_actual(
        self,
        actuals: Union[float, List[float]],
        user_id: Optional[PredictionIdentifier] = None,
        aporia_id: Optional[int] = None,
    ):
        """Logs a single prediction actual values.

        Use this function to report the actual value (ground truth) of a previously reported prediction.
        The ground truth will be used by Aporia to calculate model's performance. Either user_id or
        aporia_id must be reported, but not both.

        Args:
            actuals (Union[float, List[float]]): Prediction actual values
            user_id (PredictionIdentifier, optional): An unique identifier of the prediction which
                was provided by the the user during the prediction report. Defaults to None.
            aporia_id (int, optional): An unique identifier of the prediction which was automatically generated
                by Aporia during the prediction report. Defaults to None.
        """
        try:
            self.log_actual_batch(
                user_ids=None if user_id is None else [user_id],
                aporia_ids=None if aporia_id is None else [aporia_id],
                actuals=[convert_to_list(convert_scalar_to_iterable(actuals))],
            )
        except Exception as err:
            handle_error(
                message="Logging actual failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=False,
                original_exception=err,
                log_level=logging.ERROR,
            )

    def log_actual_batch(
        self,
        actuals: List[List[float]],
        user_ids: Optional[List[PredictionIdentifier]] = None,
        aporia_ids: Optional[List[int]] = None,
    ):
        """Logs multiple predictions actual values.

            Use this function to report the actual values (ground truth) of a previously reported predictions.
            The ground truth will be used by Aporia to calculate model's performance. Either user_ids or
            aporia_ids must be reported, but not both.

        Args:
            actuals (List[List[float]]): Predictions actual values for each prediction
            user_ids (List[PredictionIdentifier], optional): A list of unique identifiers of the prediction,
                which were provided by the the user during the prediction report. Defaults to None.
            aporia_ids (List[int], optional): A list of unique identifiers of the prediction,
                which were automatically generated by Aporia during the prediction report. Defaults to None.
        """
        if not self._model_ready:
            return

        if not self._model_version_exists:
            logger.warning(
                "Logging actual failed: features for this model version were not reported."
            )
            return

        logger.debug("Logging {} actual values".format(len(actuals)))
        try:
            actuals = convert_list_members_to_lists(convert_to_list(actuals))

            if not is_valid_log_actual_input(
                user_ids=user_ids,
                aporia_ids=aporia_ids,
                actuals=actuals,
            ):
                logger.warning("Logging actual values failed: Invalid input.")
                return

            self._event_loop.run_coroutine(
                coro=self._log_actual_batch(
                    user_ids=user_ids,
                    aporia_ids=aporia_ids,
                    actuals=actuals,
                ),
                await_result=False,
            )
        except Exception as err:
            handle_error(
                message="Logging actual values batch failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=False,
                original_exception=err,
                log_level=logging.ERROR,
            )

    async def _log_actual_batch(
        self,
        actuals: List[List[float]],
        user_ids: Optional[List[PredictionIdentifier]] = None,
        aporia_ids: Optional[List[int]] = None,
    ):
        try:
            await report_actual_batch(
                graphql_client=self._graphql_client,
                model_id=self.model_id,
                model_version=self.model_version,
                environment=self._environment,
                user_ids=user_ids,
                aporia_ids=aporia_ids,
                actuals=actuals,
            )
        except Exception as err:
            handle_error(
                message="Logging actual batch failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=False,
                original_exception=err,
                log_level=logging.ERROR,
            )

    def log_json(self, data: Any):
        """Logs arbitrary data.

        Args:
            data (Any): Data to log, must be JSON serializable
        """
        if not self._model_ready:
            return

        logger.debug("Logging arbitrary data.")
        try:
            self._event_loop.run_coroutine(
                coro=self._log_json(data=data),
                await_result=False,
            )
        except Exception as err:
            handle_error(
                message="Logging arbitrary data failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=False,
                original_exception=err,
                log_level=logging.ERROR,
            )

    async def _log_json(self, data: Any):
        try:
            await log_json(
                graphql_client=self._graphql_client,
                model_id=self.model_id,
                model_version=self.model_version,
                environment=self._environment,
                data=data,
            )
        except Exception as err:
            handle_error(
                message="Logging arbitrary data failed, error: {}".format(str(err)),
                add_trace=self._debug,
                raise_exception=False,
                original_exception=err,
                log_level=logging.ERROR,
            )


class Model(BaseModel):
    """Model object."""

    def __init__(self, model_id: str, model_version: str):
        """Initializes a Model object.

        Args:
            model_id (str): Model identifier, as received from the Aporia dashboard.
            model_version (str): Model version - this can be any string that represents the model
                version, such as "v1" or a git commit hash.
        """
        if aporia.context is None:
            logger.error("Aporia was not initialized.")
            super().__init__(
                model_id=model_id,
                model_version=model_version,
                graphql_client=None,
                environment=None,
                event_loop=None,
                debug=False,
                throw_errors=False,
                timeout=None,
            )
        else:
            super().__init__(
                model_id=model_id,
                model_version=model_version,
                graphql_client=aporia.context.graphql_client,
                event_loop=aporia.context.event_loop,
                environment=aporia.context.config.environment,
                debug=aporia.context.config.debug,
                throw_errors=aporia.context.config.throw_errors,
                timeout=aporia.context.config.blocking_call_timeout,
            )
