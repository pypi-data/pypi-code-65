from dataclasses import dataclass, field
from typing import Type, List, Union

from snowday.context.base import ContextFunction
from snowday.exceptions import InvalidParamsException
from snowday.objects.account import AwsApiIntegration, Warehouse
from snowday.objects.base import BaseSnowflakeObject
from snowday.objects.base_schema import SchemaObject
from snowday.objects.database import Schema
from snowday.objects.helper import Range
from snowday.objects.table import Table, ACCEPTED_TABLE_COLUMNS
from snowday.types.base import DataType, Sql, CronSchedule, SessionParameter

from snowday.types import ALL_TYPES


@dataclass
class Task(SchemaObject):
    as_sql: Sql
    warehouse: Warehouse
    wait_time_minutes: int = None
    cron_schedule: CronSchedule = None
    cron_timezone: str = None  # FIXME! Should this be typed?
    session_parameters: List[SessionParameter] = None
    user_task_timeout_ms: int = 3600000
    when: Union[Type["StreamHasData"]] = None  # B/c otherwise circular import
    after: Type["Task"] = None  # B/c self-referencing.
    copy_grants: bool = False

    def _validate(self):
        # both wait_time_minutes and cron_* cannot be defined
        # if cron_schedule is defined then cron_timezone should be as well.
        if self.wait_time_minutes and self.cron_schedule:
            raise InvalidParamsException(
                "Wait time and cron schedule cannot both be defined. Please use one or the other."
            )
        if self.cron_schedule and not self.cron_timezone:
            raise InvalidParamsException(
                "Cron schedule and cron timezone must both be defined."
            )
        # FIXME! wait_time_minutes, cron_*, when, and after are mutually exclusive and should be validated as such.

    @property
    def _settings_str(self):
        if self.wait_time_minutes:
            schedule_str = f"schedule = '{self.wait_time_minutes} minute'"
        elif self.cron_schedule and self.cron_timezone:
            schedule_str = (
                f"schedule = 'using cron {self.cron_schedule} {self.cron_timezone}' "
            )
        return (
            f"warehouse = {self.warehouse.name} "
            f"{schedule_str} "
            f"as {self.as_sql.statement}"
        )


@dataclass
class View(SchemaObject):
    pass


@dataclass
class MaterializedView(SchemaObject):
    pass


@dataclass
class MaskingPolicy(SchemaObject):
    val: str
    val_data_type: DataType
    returns_data_type: DataType
    expression: Sql

    def __post_init__(self):
        if self.val_data_type not in ALL_TYPES:
            raise InvalidParamsException(
                f"{self.val_data_type} is not in the list of supported snowflake types: {ALL_TYPES}"
            )
        if self.returns_data_type not in ALL_TYPES:
            raise InvalidParamsException(
                f"{self.returns_data_type} is not in the list of supported snowflake types: {ALL_TYPES}"
            )

    @property
    def _settings_str(self):
        return f"as ({self.val} {self.val_data_type}) returns {self.returns_data_type} -> {self.expression.statement}"


@dataclass
class FileFormat(SchemaObject):
    pass


@dataclass
class InternalStage(SchemaObject):
    pass


@dataclass
class ExternalStage(SchemaObject):
    pass


@dataclass
class Pipe(SchemaObject):
    auto_ingest: bool
    aws_sns_topic: str
    integration: str
    copy_statement: str

    def __post_init__(self):
        # https://docs.snowflake.com/en/sql-reference/sql/create-pipe.html
        raise Exception("FIXME PLZ!!!!")


@dataclass
class Stream(SchemaObject):
    table: Table
    append_only: bool
    copy_grants: bool = False
    range: Range = None

    def __post_init__(self):
        # https://docs.snowflake.com/en/sql-reference/sql/create-stream.html
        raise Exception("FIXME PLZ!!!!")


@dataclass
class FunctionArg:
    name: str
    data_type: str

    def _validate(self):
        if self.data_type not in ALL_TYPES:
            raise InvalidParamsException(
                f"{self.data_type} not in list of accepted snowflake data types: {ALL_TYPES}"
            )

    @property
    def sql(self):
        return f"{self.name}, {self.data_type}"


@dataclass
class Function(SchemaObject):
    args: List[FunctionArg]
    returns_data_type: DataType
    columns: List[ACCEPTED_TABLE_COLUMNS]
    function_definition: str  # Must be valid SQL or Javascript

    def _validate(self):
        if self.data_type not in ALL_TYPES:
            raise InvalidParamsException(
                f"{self.returns_data_type} not in list of accepted snowflake data types: {ALL_TYPES}"
            )


@dataclass
class ExternalFunctionHeader:
    name: str
    value: str


@dataclass
class ExternalFunction(SchemaObject):
    args: List[FunctionArg]
    returns_data_type: DataType
    returns_null: bool
    category: str  # either volatile or immutable
    is_secure: bool
    api_integration: AwsApiIntegration
    headers: List[ExternalFunctionHeader]
    context_headers: List[ContextFunction]
    max_batch_rows: int
    compression: str  # NONE, AUTO, GZIP, DEFLATE
    url: str


@dataclass
class Procedure(SchemaObject):
    pass


@dataclass
class Sequence(SchemaObject):
    # https://docs.snowflake.com/en/sql-reference/sql/create-sequence.html
    start_with: int
    increment_by: int = 1

    @property
    def _settings_str(self):
        return f"with start={self.start_with} increment={self.increment_by} comment='{self.comment}'"
