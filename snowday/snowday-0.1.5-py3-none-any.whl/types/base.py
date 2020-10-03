from dataclasses import dataclass
from snowday.exceptions import InvalidParamsException
from typing import List, Type


VALID_TIME_UNITS = [
    "days",
    "hours",
    "minutes",
    "seconds",
    "milliseconds",
    "microseconds",
    "nanoseconds",
]


@dataclass
class DataType:
    name: str

    @property
    def sql(self):
        # FIXME! Validate `name` is actually a thing
        return name


@dataclass
class Sql:
    statement: str

    def __post_init__(self):
        # FIXME! Ensure sql is valid.
        pass

    def __add__(self, more: Type["Sql"]):
        return Sql(statement=f"{self.statement} {more.statement}")


@dataclass
class QueryResult:
    """By wrapping the results of a DictCursor,
    significant future flexibility is intrinsic.
    Want to set k, v pairs as attrs? Can do.
    Want to provide query result validation? Can do.
    """

    result: dict
    as_attrs: bool = True

    # Like this ;)
    def __post_init__(self):
        if self.result and self.as_attrs:
            for k, v in self.result.items():
                setattr(self, k.lower(), v)


@dataclass
class QueryResultSet:
    results: List[QueryResult]


@dataclass
class Js:
    """I can't believe I'm doing this I can't believe I'm doing this I can't....
    """

    statement: str

    def __post_init__(self):
        # FIXME! Ensure javascript is valid
        pass


@dataclass
class CronSchedule:
    schedule: str

    def __post_init__(self):
        # FIXME! Validate the schedule is a proper cron expression
        pass


@dataclass
class Session:
    id: str


@dataclass
class SessionParameter:
    name: str
    value: str

    @property
    def sql(self):
        return Sql(statement=f"{self.name}='{self.value}'")

    @property
    def set(self):
        return Sql(statement=f"alter session set {self.name}='{self.value}'")


@dataclass
class Transaction:
    id: str


@dataclass
class Query:
    id: str


@dataclass
class ExplainJson:
    """The output of system$explain_plan_json
    """

    output: str


@dataclass
class TimeUnit:
    unit: str

    def __post_init__(self):
        self.unit = self.unit.lower()
        if self.unit not in VALID_TIME_UNITS:
            raise InvalidParamsException(
                f"{self.unit} is not a valid unit: {VALID_TIME_UNITS}"
            )


@dataclass
class SnsTopic:
    arn: str
