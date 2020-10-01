"""Structured representations of system events."""
import logging
import os
from collections import namedtuple
from enum import Enum

from dagster import check
from dagster.core.definitions import (
    AssetMaterialization,
    EventMetadataEntry,
    ExpectationResult,
    Materialization,
    SolidHandle,
    TypeCheck,
)
from dagster.core.definitions.events import ObjectStoreOperationType
from dagster.core.execution.context.system import (
    HookContext,
    SystemExecutionContext,
    SystemStepExecutionContext,
)
from dagster.core.execution.plan.objects import StepOutputData
from dagster.core.log_manager import DagsterLogManager
from dagster.serdes import register_serdes_tuple_fallbacks, whitelist_for_serdes
from dagster.utils.error import SerializableErrorInfo, serializable_error_info_from_exc_info
from dagster.utils.timing import format_duration


class DagsterEventType(Enum):
    """The types of events that may be yielded by solid and pipeline execution."""

    STEP_OUTPUT = "STEP_OUTPUT"
    STEP_INPUT = "STEP_INPUT"
    STEP_FAILURE = "STEP_FAILURE"
    STEP_START = "STEP_START"
    STEP_SUCCESS = "STEP_SUCCESS"
    STEP_SKIPPED = "STEP_SKIPPED"

    STEP_UP_FOR_RETRY = "STEP_UP_FOR_RETRY"  # "failed" but want to retry
    STEP_RESTARTED = "STEP_RESTARTED"

    STEP_MATERIALIZATION = "STEP_MATERIALIZATION"
    STEP_EXPECTATION_RESULT = "STEP_EXPECTATION_RESULT"

    PIPELINE_INIT_FAILURE = "PIPELINE_INIT_FAILURE"

    PIPELINE_START = "PIPELINE_START"
    PIPELINE_SUCCESS = "PIPELINE_SUCCESS"
    PIPELINE_FAILURE = "PIPELINE_FAILURE"

    OBJECT_STORE_OPERATION = "OBJECT_STORE_OPERATION"

    ENGINE_EVENT = "ENGINE_EVENT"

    HOOK_COMPLETED = "HOOK_COMPLETED"
    HOOK_ERRORED = "HOOK_ERRORED"
    HOOK_SKIPPED = "HOOK_SKIPPED"


STEP_EVENTS = {
    DagsterEventType.STEP_INPUT,
    DagsterEventType.STEP_START,
    DagsterEventType.STEP_OUTPUT,
    DagsterEventType.STEP_FAILURE,
    DagsterEventType.STEP_SUCCESS,
    DagsterEventType.STEP_SKIPPED,
    DagsterEventType.STEP_MATERIALIZATION,
    DagsterEventType.STEP_EXPECTATION_RESULT,
    DagsterEventType.OBJECT_STORE_OPERATION,
    DagsterEventType.STEP_RESTARTED,
    DagsterEventType.STEP_UP_FOR_RETRY,
}

FAILURE_EVENTS = {
    DagsterEventType.PIPELINE_INIT_FAILURE,
    DagsterEventType.PIPELINE_FAILURE,
    DagsterEventType.STEP_FAILURE,
}

PIPELINE_EVENTS = {
    DagsterEventType.PIPELINE_START,
    DagsterEventType.PIPELINE_SUCCESS,
    DagsterEventType.PIPELINE_FAILURE,
}

HOOK_EVENTS = {
    DagsterEventType.HOOK_COMPLETED,
    DagsterEventType.HOOK_ERRORED,
    DagsterEventType.HOOK_SKIPPED,
}


def _assert_type(method, expected_type, actual_type):
    check.invariant(
        expected_type == actual_type,
        (
            "{method} only callable when event_type is {expected_type}, called on {actual_type}"
        ).format(method=method, expected_type=expected_type, actual_type=actual_type),
    )


def _validate_event_specific_data(event_type, event_specific_data):
    from dagster.core.execution.plan.objects import StepFailureData, StepSuccessData, StepInputData

    if event_type == DagsterEventType.STEP_OUTPUT:
        check.inst_param(event_specific_data, "event_specific_data", StepOutputData)
    elif event_type == DagsterEventType.STEP_FAILURE:
        check.inst_param(event_specific_data, "event_specific_data", StepFailureData)
    elif event_type == DagsterEventType.STEP_SUCCESS:
        check.inst_param(event_specific_data, "event_specific_data", StepSuccessData)
    elif event_type == DagsterEventType.STEP_MATERIALIZATION:
        check.inst_param(event_specific_data, "event_specific_data", StepMaterializationData)
    elif event_type == DagsterEventType.STEP_EXPECTATION_RESULT:
        check.inst_param(event_specific_data, "event_specific_data", StepExpectationResultData)
    elif event_type == DagsterEventType.STEP_INPUT:
        check.inst_param(event_specific_data, "event_specific_data", StepInputData)
    elif event_type == DagsterEventType.ENGINE_EVENT:
        check.inst_param(event_specific_data, "event_specific_data", EngineEventData)
    elif event_type == DagsterEventType.HOOK_ERRORED:
        check.inst_param(event_specific_data, "event_specific_data", HookErroredData)

    return event_specific_data


def log_step_event(step_context, event):
    check.inst_param(step_context, "step_context", SystemStepExecutionContext)
    check.inst_param(event, "event", DagsterEvent)

    event_type = DagsterEventType(event.event_type_value)
    log_fn = step_context.log.error if event_type in FAILURE_EVENTS else step_context.log.debug

    log_fn(
        event.message
        or "{event_type} for step {step_key}".format(
            event_type=event_type, step_key=step_context.step.key
        ),
        dagster_event=event,
        pipeline_name=step_context.pipeline_def.name,
    )


def log_pipeline_event(pipeline_context, event, step_key):
    event_type = DagsterEventType(event.event_type_value)

    log_fn = (
        pipeline_context.log.error if event_type in FAILURE_EVENTS else pipeline_context.log.debug
    )

    log_fn(
        event.message
        or "{event_type} for pipeline {pipeline_name}".format(
            event_type=event_type, pipeline_name=pipeline_context.pipeline_def.name
        ),
        dagster_event=event,
        pipeline_name=pipeline_context.pipeline_def.name,
        step_key=step_key,
    )


def log_resource_event(log_manager, pipeline_name, event):
    check.inst_param(log_manager, "log_manager", DagsterLogManager)
    check.inst_param(event, "event", DagsterEvent)
    check.inst(event.event_specific_data, EngineEventData)

    log_fn = log_manager.error if event.event_specific_data.error else log_manager.debug
    log_fn(event.message, dagster_event=event, pipeline_name=pipeline_name, step_key=event.step_key)


@whitelist_for_serdes
class DagsterEvent(
    namedtuple(
        "_DagsterEvent",
        "event_type_value pipeline_name step_key solid_handle step_kind_value "
        "logging_tags event_specific_data message pid",
    )
):
    """Events yielded by solid and pipeline execution.

    Users should not instantiate this class.

    Attributes:
        event_type_value (str): Value for a DagsterEventType.
        pipeline_name (str)
        step_key (str)
        solid_handle (SolidHandle)
        step_kind_value (str): Value for a StepKind.
        logging_tags (Dict[str, str])
        event_specific_data (Any): Type must correspond to event_type_value.
        message (str)
        pid (int)
    """

    @staticmethod
    def from_step(event_type, step_context, event_specific_data=None, message=None):

        check.inst_param(step_context, "step_context", SystemStepExecutionContext)

        event = DagsterEvent(
            check.inst_param(event_type, "event_type", DagsterEventType).value,
            step_context.pipeline_def.name,
            step_context.step.key,
            step_context.step.solid_handle,
            step_context.step.kind.value,
            step_context.logging_tags,
            _validate_event_specific_data(event_type, event_specific_data),
            check.opt_str_param(message, "message"),
            pid=os.getpid(),
        )

        log_step_event(step_context, event)

        return event

    @staticmethod
    def from_pipeline(
        event_type, pipeline_context, message=None, event_specific_data=None, step_key=None
    ):
        check.inst_param(pipeline_context, "pipeline_context", SystemExecutionContext)

        pipeline_name = pipeline_context.pipeline_def.name

        event = DagsterEvent(
            check.inst_param(event_type, "event_type", DagsterEventType).value,
            check.str_param(pipeline_name, "pipeline_name"),
            message=check.opt_str_param(message, "message"),
            event_specific_data=_validate_event_specific_data(event_type, event_specific_data),
            step_key=step_key,
            pid=os.getpid(),
        )

        log_pipeline_event(pipeline_context, event, step_key)

        return event

    @staticmethod
    def from_resource(execution_plan, log_manager, message=None, event_specific_data=None):
        from dagster.core.execution.plan.plan import ExecutionPlan

        check.inst_param(execution_plan, "execution_plan", ExecutionPlan)
        pipeline_name = execution_plan.pipeline_def.name
        event = DagsterEvent(
            DagsterEventType.ENGINE_EVENT.value,
            pipeline_name=pipeline_name,
            message=check.opt_str_param(message, "message"),
            event_specific_data=_validate_event_specific_data(
                DagsterEventType.ENGINE_EVENT, event_specific_data
            ),
            step_key=execution_plan.step_key_for_single_step_plans(),
            pid=os.getpid(),
        )
        log_resource_event(log_manager, pipeline_name, event)
        return event

    def __new__(
        cls,
        event_type_value,
        pipeline_name,
        step_key=None,
        solid_handle=None,
        step_kind_value=None,
        logging_tags=None,
        event_specific_data=None,
        message=None,
        pid=None,
    ):
        event_type_value, event_specific_data = _handle_back_compat(
            event_type_value, event_specific_data
        )

        return super(DagsterEvent, cls).__new__(
            cls,
            check.str_param(event_type_value, "event_type_value"),
            check.str_param(pipeline_name, "pipeline_name"),
            check.opt_str_param(step_key, "step_key"),
            check.opt_inst_param(solid_handle, "solid_handle", SolidHandle),
            check.opt_str_param(step_kind_value, "step_kind_value"),
            check.opt_dict_param(logging_tags, "logging_tags"),
            _validate_event_specific_data(DagsterEventType(event_type_value), event_specific_data),
            check.opt_str_param(message, "message"),
            check.opt_int_param(pid, "pid"),
        )

    @property
    def solid_name(self):
        return self.solid_handle.name

    @property
    def event_type(self):
        """DagsterEventType: The type of this event."""
        return DagsterEventType(self.event_type_value)

    @property
    def is_step_event(self):
        return self.event_type in STEP_EVENTS

    @property
    def is_hook_event(self):
        return self.event_type in HOOK_EVENTS

    @property
    def step_kind(self):
        from dagster.core.execution.plan.objects import StepKind

        return StepKind(self.step_kind_value)

    @property
    def is_step_success(self):
        return self.event_type == DagsterEventType.STEP_SUCCESS

    @property
    def is_successful_output(self):
        return self.event_type == DagsterEventType.STEP_OUTPUT

    @property
    def is_step_start(self):
        return self.event_type == DagsterEventType.STEP_START

    @property
    def is_step_failure(self):
        return self.event_type == DagsterEventType.STEP_FAILURE

    @property
    def is_step_skipped(self):
        return self.event_type == DagsterEventType.STEP_SKIPPED

    @property
    def is_step_up_for_retry(self):
        return self.event_type == DagsterEventType.STEP_UP_FOR_RETRY

    @property
    def is_step_restarted(self):
        return self.event_type == DagsterEventType.STEP_RESTARTED

    @property
    def is_pipeline_success(self):
        return self.event_type == DagsterEventType.PIPELINE_SUCCESS

    @property
    def is_pipeline_failure(self):
        return self.event_type == DagsterEventType.PIPELINE_FAILURE

    @property
    def is_pipeline_init_failure(self):
        return self.event_type == DagsterEventType.PIPELINE_INIT_FAILURE

    @property
    def is_failure(self):
        return self.event_type in FAILURE_EVENTS

    @property
    def is_pipeline_event(self):
        return self.event_type in PIPELINE_EVENTS

    @property
    def is_engine_event(self):
        return self.event_type == DagsterEventType.ENGINE_EVENT

    @property
    def asset_key(self):
        if self.event_type != DagsterEventType.STEP_MATERIALIZATION:
            return None
        return self.step_materialization_data.materialization.asset_key

    @property
    def step_input_data(self):
        _assert_type("step_input_data", DagsterEventType.STEP_INPUT, self.event_type)
        return self.event_specific_data

    @property
    def step_output_data(self):
        _assert_type("step_output_data", DagsterEventType.STEP_OUTPUT, self.event_type)
        return self.event_specific_data

    @property
    def step_success_data(self):
        _assert_type("step_success_data", DagsterEventType.STEP_SUCCESS, self.event_type)
        return self.event_specific_data

    @property
    def step_failure_data(self):
        _assert_type("step_failure_data", DagsterEventType.STEP_FAILURE, self.event_type)
        return self.event_specific_data

    @property
    def step_retry_data(self):
        _assert_type("step_retry_data", DagsterEventType.STEP_UP_FOR_RETRY, self.event_type)
        return self.event_specific_data

    @property
    def step_materialization_data(self):
        _assert_type(
            "step_materialization_data", DagsterEventType.STEP_MATERIALIZATION, self.event_type
        )
        return self.event_specific_data

    @property
    def step_expectation_result_data(self):
        _assert_type(
            "step_expectation_result_data",
            DagsterEventType.STEP_EXPECTATION_RESULT,
            self.event_type,
        )
        return self.event_specific_data

    @property
    def pipeline_init_failure_data(self):
        _assert_type(
            "pipeline_init_failure_data", DagsterEventType.PIPELINE_INIT_FAILURE, self.event_type
        )
        return self.event_specific_data

    @property
    def engine_event_data(self):
        _assert_type("engine_event_data", DagsterEventType.ENGINE_EVENT, self.event_type)
        return self.event_specific_data

    @property
    def hook_completed_data(self):
        _assert_type("hook_completed_data", DagsterEventType.HOOK_COMPLETED, self.event_type)
        return self.event_specific_data

    @property
    def hook_errored_data(self):
        _assert_type("hook_errored_data", DagsterEventType.HOOK_ERRORED, self.event_type)
        return self.event_specific_data

    @property
    def hook_skipped_data(self):
        _assert_type("hook_skipped_data", DagsterEventType.HOOK_SKIPPED, self.event_type)
        return self.event_specific_data

    @staticmethod
    def step_output_event(step_context, step_output_data):
        check.inst_param(step_output_data, "step_output_data", StepOutputData)
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_OUTPUT,
            step_context=step_context,
            event_specific_data=step_output_data,
            message='Yielded output "{output_name}" of type "{output_type}".{type_check_clause}'.format(
                output_name=step_output_data.step_output_handle.output_name,
                output_type=step_context.step.step_output_named(
                    step_output_data.step_output_handle.output_name
                ).dagster_type.display_name,
                type_check_clause=(
                    " Warning! Type check failed."
                    if not step_output_data.type_check_data.success
                    else " (Type check passed)."
                )
                if step_output_data.type_check_data
                else " (No type check).",
            ),
        )

    @staticmethod
    def step_failure_event(step_context, step_failure_data):
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_FAILURE,
            step_context=step_context,
            event_specific_data=step_failure_data,
            message='Execution of step "{step_key}" failed.'.format(step_key=step_context.step.key),
        )

    @staticmethod
    def step_retry_event(step_context, step_retry_data):
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_UP_FOR_RETRY,
            step_context=step_context,
            event_specific_data=step_retry_data,
            message='Execution of step "{step_key}" failed and has requested a retry{wait_str}.'.format(
                step_key=step_context.step.key,
                wait_str=" in {n} seconds".format(n=step_retry_data.seconds_to_wait)
                if step_retry_data.seconds_to_wait
                else "",
            ),
        )

    @staticmethod
    def step_input_event(step_context, step_input_data):
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_INPUT,
            step_context=step_context,
            event_specific_data=step_input_data,
            message='Got input "{input_name}" of type "{input_type}".{type_check_clause}'.format(
                input_name=step_input_data.input_name,
                input_type=step_context.step.step_input_named(
                    step_input_data.input_name
                ).dagster_type.display_name,
                type_check_clause=(
                    " Warning! Type check failed."
                    if not step_input_data.type_check_data.success
                    else " (Type check passed)."
                )
                if step_input_data.type_check_data
                else " (No type check).",
            ),
        )

    @staticmethod
    def step_start_event(step_context):
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_START,
            step_context=step_context,
            message='Started execution of step "{step_key}".'.format(
                step_key=step_context.step.key
            ),
        )

    @staticmethod
    def step_restarted_event(step_context, previous_attempts):
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_RESTARTED,
            step_context=step_context,
            message='Started re-execution (attempt # {n}) of step "{step_key}".'.format(
                step_key=step_context.step.key, n=previous_attempts + 1
            ),
        )

    @staticmethod
    def step_success_event(step_context, success):
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_SUCCESS,
            step_context=step_context,
            event_specific_data=success,
            message='Finished execution of step "{step_key}" in {duration}.'.format(
                # TODO: Make duration human readable
                # See: https://github.com/dagster-io/dagster/issues/1602
                step_key=step_context.step.key,
                duration=format_duration(success.duration_ms),
            ),
        )

    @staticmethod
    def step_skipped_event(step_context):
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_SKIPPED,
            step_context=step_context,
            message='Skipped execution of step "{step_key}".'.format(
                step_key=step_context.step.key
            ),
        )

    @staticmethod
    def step_materialization(step_context, materialization):
        check.inst_param(
            materialization, "materialization", (AssetMaterialization, Materialization)
        )
        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_MATERIALIZATION,
            step_context=step_context,
            event_specific_data=StepMaterializationData(materialization),
            message=materialization.description
            if materialization.description
            else "Materialized value{label_clause}.".format(
                label_clause=" {label}".format(label=materialization.label)
                if materialization.label
                else ""
            ),
        )

    @staticmethod
    def step_expectation_result(step_context, expectation_result):
        check.inst_param(expectation_result, "expectation_result", ExpectationResult)

        def _msg():
            if expectation_result.description:
                return expectation_result.description

            return "Expectation{label_clause} {result_verb}".format(
                label_clause=" " + expectation_result.label if expectation_result.label else "",
                result_verb="passed" if expectation_result.success else "failed",
            )

        return DagsterEvent.from_step(
            event_type=DagsterEventType.STEP_EXPECTATION_RESULT,
            step_context=step_context,
            event_specific_data=StepExpectationResultData(expectation_result),
            message=_msg(),
        )

    @staticmethod
    def pipeline_start(pipeline_context):
        return DagsterEvent.from_pipeline(
            DagsterEventType.PIPELINE_START,
            pipeline_context,
            message='Started execution of pipeline "{pipeline_name}".'.format(
                pipeline_name=pipeline_context.pipeline_def.name
            ),
        )

    @staticmethod
    def pipeline_success(pipeline_context):
        return DagsterEvent.from_pipeline(
            DagsterEventType.PIPELINE_SUCCESS,
            pipeline_context,
            message='Finished execution of pipeline "{pipeline_name}".'.format(
                pipeline_name=pipeline_context.pipeline_def.name
            ),
        )

    @staticmethod
    def pipeline_failure(pipeline_context):
        return DagsterEvent.from_pipeline(
            DagsterEventType.PIPELINE_FAILURE,
            pipeline_context,
            message='Execution of pipeline "{pipeline_name}" failed.'.format(
                pipeline_name=pipeline_context.pipeline_def.name
            ),
        )

    @staticmethod
    def resource_init_start(execution_plan, log_manager, resource_keys):
        from dagster.core.execution.plan.plan import ExecutionPlan

        return DagsterEvent.from_resource(
            execution_plan=check.inst_param(execution_plan, "execution_plan", ExecutionPlan),
            log_manager=check.inst_param(log_manager, "log_manager", DagsterLogManager),
            message="Starting initialization of resources [{}].".format(", ".join(resource_keys)),
            event_specific_data=EngineEventData(metadata_entries=[], marker_start="resources"),
        )

    @staticmethod
    def resource_init_success(execution_plan, log_manager, resource_instances, resource_init_times):
        from dagster.core.execution.plan.plan import ExecutionPlan

        metadata_entries = []
        for resource_key in resource_instances.keys():
            resource_obj = resource_instances[resource_key]
            resource_time = resource_init_times[resource_key]
            metadata_entries.append(
                EventMetadataEntry.python_artifact(
                    resource_obj.__class__, resource_key, "Initialized in {}".format(resource_time)
                )
            )

        return DagsterEvent.from_resource(
            execution_plan=check.inst_param(execution_plan, "execution_plan", ExecutionPlan),
            log_manager=check.inst_param(log_manager, "log_manager", DagsterLogManager),
            message="Finished initialization of resources [{}].".format(
                ", ".join(resource_init_times.keys())
            ),
            event_specific_data=EngineEventData(
                metadata_entries=metadata_entries, marker_end="resources",
            ),
        )

    @staticmethod
    def resource_init_failure(execution_plan, log_manager, resource_keys, error):
        from dagster.core.execution.plan.plan import ExecutionPlan

        return DagsterEvent.from_resource(
            execution_plan=check.inst_param(execution_plan, "execution_plan", ExecutionPlan),
            log_manager=check.inst_param(log_manager, "log_manager", DagsterLogManager),
            message="Initialization of resources [{}] failed.".format(", ".join(resource_keys)),
            event_specific_data=EngineEventData(
                metadata_entries=[], marker_end="resources", error=error,
            ),
        )

    @staticmethod
    def resource_teardown_failure(execution_plan, log_manager, resource_keys, error):
        from dagster.core.execution.plan.plan import ExecutionPlan

        return DagsterEvent.from_resource(
            execution_plan=check.inst_param(execution_plan, "execution_plan", ExecutionPlan),
            log_manager=check.inst_param(log_manager, "log_manager", DagsterLogManager),
            message="Teardown of resources [{}] failed.".format(", ".join(resource_keys)),
            event_specific_data=EngineEventData(
                metadata_entries=[], marker_start=None, marker_end=None, error=error,
            ),
        )

    @staticmethod
    def pipeline_init_failure(pipeline_name, failure_data, log_manager):
        check.inst_param(failure_data, "failure_data", PipelineInitFailureData)
        check.inst_param(log_manager, "log_manager", DagsterLogManager)
        # this failure happens trying to bring up context so can't use from_pipeline

        event = DagsterEvent(
            event_type_value=DagsterEventType.PIPELINE_INIT_FAILURE.value,
            pipeline_name=pipeline_name,
            event_specific_data=failure_data,
            message=(
                'Pipeline failure during initialization of pipeline "{pipeline_name}". '
                "This may be due to a failure in initializing a resource or logger."
            ).format(pipeline_name=pipeline_name),
            pid=os.getpid(),
        )
        log_manager.error(
            event.message
            or "{event_type} for pipeline {pipeline_name}".format(
                event_type=DagsterEventType.PIPELINE_INIT_FAILURE, pipeline_name=pipeline_name
            ),
            dagster_event=event,
            pipeline_name=pipeline_name,
        )
        return event

    @staticmethod
    def engine_event(pipeline_context, message, event_specific_data=None, step_key=None):
        return DagsterEvent.from_pipeline(
            DagsterEventType.ENGINE_EVENT,
            pipeline_context,
            message,
            event_specific_data=event_specific_data,
            step_key=step_key,
        )

    @staticmethod
    def object_store_operation(step_context, object_store_operation_result):
        object_store_name = (
            "{object_store_name} ".format(
                object_store_name=object_store_operation_result.object_store_name
            )
            if object_store_operation_result.object_store_name
            else ""
        )

        serialization_strategy_modifier = (
            " using {serialization_strategy_name}".format(
                serialization_strategy_name=object_store_operation_result.serialization_strategy_name
            )
            if object_store_operation_result.serialization_strategy_name
            else ""
        )

        value_name = object_store_operation_result.value_name

        if (
            ObjectStoreOperationType(object_store_operation_result.op)
            == ObjectStoreOperationType.SET_OBJECT
        ):
            message = (
                "Stored intermediate object for output {value_name} in "
                "{object_store_name}object store{serialization_strategy_modifier}."
            ).format(
                value_name=value_name,
                object_store_name=object_store_name,
                serialization_strategy_modifier=serialization_strategy_modifier,
            )
        elif (
            ObjectStoreOperationType(object_store_operation_result.op)
            == ObjectStoreOperationType.GET_OBJECT
        ):
            message = (
                "Retrieved intermediate object for input {value_name} in "
                "{object_store_name}object store{serialization_strategy_modifier}."
            ).format(
                value_name=value_name,
                object_store_name=object_store_name,
                serialization_strategy_modifier=serialization_strategy_modifier,
            )
        elif (
            ObjectStoreOperationType(object_store_operation_result.op)
            == ObjectStoreOperationType.CP_OBJECT
        ):
            message = (
                "Copied intermediate object for input {value_name} from {key} to {dest_key}"
            ).format(
                value_name=value_name,
                key=object_store_operation_result.key,
                dest_key=object_store_operation_result.dest_key,
            )
        else:
            message = ""

        return DagsterEvent.from_step(
            DagsterEventType.OBJECT_STORE_OPERATION,
            step_context,
            event_specific_data=ObjectStoreOperationResultData(
                op=object_store_operation_result.op,
                value_name=value_name,
                metadata_entries=[
                    EventMetadataEntry.path(object_store_operation_result.key, label="key")
                ],
            ),
            message=message,
        )

    @staticmethod
    def hook_completed(hook_context, hook_def):
        event_type = DagsterEventType.HOOK_COMPLETED
        check.inst_param(hook_context, "hook_context", HookContext)

        event = DagsterEvent(
            event_type_value=event_type.value,
            pipeline_name=hook_context.pipeline_def.name,
            step_key=hook_context.step.key,
            solid_handle=hook_context.step.solid_handle,
            step_kind_value=hook_context.step.kind.value,
            logging_tags=hook_context.logging_tags,
            message=(
                'Finished the execution of hook "{hook_name}" triggered for solid "{solid_name}".'
            ).format(hook_name=hook_def.name, solid_name=hook_context.solid.name),
        )

        hook_context.log.debug(
            event.message, dagster_event=event, pipeline_name=hook_context.pipeline_def.name,
        )

        return event

    @staticmethod
    def hook_errored(hook_context, error):
        event_type = DagsterEventType.HOOK_ERRORED
        check.inst_param(hook_context, "hook_context", HookContext)

        event = DagsterEvent(
            event_type_value=event_type.value,
            pipeline_name=hook_context.pipeline_def.name,
            step_key=hook_context.step.key,
            solid_handle=hook_context.step.solid_handle,
            step_kind_value=hook_context.step.kind.value,
            logging_tags=hook_context.logging_tags,
            event_specific_data=_validate_event_specific_data(
                event_type,
                HookErroredData(
                    error=serializable_error_info_from_exc_info(error.original_exc_info)
                ),
            ),
        )

        hook_context.log.error(
            str(error), dagster_event=event, pipeline_name=hook_context.pipeline_def.name,
        )

        return event

    @staticmethod
    def hook_skipped(hook_context, hook_def):
        event_type = DagsterEventType.HOOK_SKIPPED
        check.inst_param(hook_context, "hook_context", HookContext)

        event = DagsterEvent(
            event_type_value=event_type.value,
            pipeline_name=hook_context.pipeline_def.name,
            step_key=hook_context.step.key,
            solid_handle=hook_context.step.solid_handle,
            step_kind_value=hook_context.step.kind.value,
            logging_tags=hook_context.logging_tags,
            message=(
                'Skipped the execution of hook "{hook_name}". It did not meet its triggering '
                'condition during the execution of solid "{solid_name}".'
            ).format(hook_name=hook_def.name, solid_name=hook_context.solid.name),
        )

        hook_context.log.debug(
            event.message, dagster_event=event, pipeline_name=hook_context.pipeline_def.name,
        )

        return event


def get_step_output_event(events, step_key, output_name="result"):
    check.list_param(events, "events", of_type=DagsterEvent)
    check.str_param(step_key, "step_key")
    check.str_param(output_name, "output_name")
    for event in events:
        if (
            event.event_type == DagsterEventType.STEP_OUTPUT
            and event.step_key == step_key
            and event.step_output_data.output_name == output_name
        ):
            return event
    return None


@whitelist_for_serdes
class StepMaterializationData(namedtuple("_StepMaterializationData", "materialization")):
    pass


@whitelist_for_serdes
class StepExpectationResultData(namedtuple("_StepExpectationResultData", "expectation_result")):
    pass


@whitelist_for_serdes
class ObjectStoreOperationResultData(
    namedtuple("_ObjectStoreOperationResultData", "op value_name metadata_entries")
):
    pass


@whitelist_for_serdes
class EngineEventData(
    namedtuple("_EngineEventData", "metadata_entries error marker_start marker_end")
):
    # serdes log
    # * added optional error
    # * added marker_start / marker_end
    #
    def __new__(cls, metadata_entries=None, error=None, marker_start=None, marker_end=None):
        return super(EngineEventData, cls).__new__(
            cls,
            metadata_entries=check.opt_list_param(
                metadata_entries, "metadata_entries", EventMetadataEntry
            ),
            error=check.opt_inst_param(error, "error", SerializableErrorInfo),
            marker_start=check.opt_str_param(marker_start, "marker_start"),
            marker_end=check.opt_str_param(marker_end, "marker_end"),
        )

    @staticmethod
    def in_process(pid, step_keys_to_execute=None, marker_end=None):
        check.int_param(pid, "pid")
        check.opt_list_param(step_keys_to_execute, "step_keys_to_execute")
        return EngineEventData(
            metadata_entries=[EventMetadataEntry.text(str(pid), "pid")]
            + (
                [EventMetadataEntry.text(str(step_keys_to_execute), "step_keys")]
                if step_keys_to_execute
                else []
            ),
            marker_end=marker_end,
        )

    @staticmethod
    def multiprocess(pid, step_keys_to_execute=None):
        check.int_param(pid, "pid")
        check.opt_list_param(step_keys_to_execute, "step_keys_to_execute")
        return EngineEventData(
            metadata_entries=[EventMetadataEntry.text(str(pid), "pid")]
            + (
                [EventMetadataEntry.text(str(step_keys_to_execute), "step_keys")]
                if step_keys_to_execute
                else []
            )
        )

    @staticmethod
    def interrupted(steps_interrupted):
        check.list_param(steps_interrupted, "steps_interrupted", str)
        return EngineEventData(
            metadata_entries=[EventMetadataEntry.text(str(steps_interrupted), "steps_interrupted")]
        )

    @staticmethod
    def engine_error(error):
        check.inst_param(error, "error", SerializableErrorInfo)
        return EngineEventData(metadata_entries=[], error=error)


@whitelist_for_serdes
class PipelineInitFailureData(namedtuple("_PipelineInitFailureData", "error")):
    def __new__(cls, error):
        return super(PipelineInitFailureData, cls).__new__(
            cls, error=check.inst_param(error, "error", SerializableErrorInfo)
        )


@whitelist_for_serdes
class HookErroredData(namedtuple("_HookErroredData", "error")):
    def __new__(cls, error):
        return super(HookErroredData, cls).__new__(
            cls, error=check.inst_param(error, "error", SerializableErrorInfo),
        )


###################################################################################################
# THE GRAVEYARD
#
#            -|-
#             |
#        _-'~~~~~`-_
#      .'           '.
#      |    R I P    |
#      |             |
#      |  Synthetic  |
#      |   Process   |
#      |   Events    |
#      |             |
###################################################################################################


def _handle_back_compat(event_type_value, event_specific_data):
    if event_type_value == "PIPELINE_PROCESS_START":
        return DagsterEventType.ENGINE_EVENT.value, EngineEventData([])
    elif event_type_value == "PIPELINE_PROCESS_STARTED":
        return DagsterEventType.ENGINE_EVENT.value, EngineEventData([])
    elif event_type_value == "PIPELINE_PROCESS_EXITED":
        return DagsterEventType.ENGINE_EVENT.value, EngineEventData([])
    else:
        return event_type_value, event_specific_data


register_serdes_tuple_fallbacks(
    {
        "PipelineProcessStartedData": None,
        "PipelineProcessExitedData": None,
        "PipelineProcessStartData": None,
    }
)
