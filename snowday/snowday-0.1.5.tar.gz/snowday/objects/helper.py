from dataclasses import dataclass
from datetime import datetime

from snowday.exceptions import InvalidParamsException

AT_BEFORE = ["at", "before"]
RANGE_PARAMS = ["timestamp", "offset", "statement"]


@dataclass
class Range:
    at_or_before: str
    timestamp: datetime = None
    offset: int = None
    statement: str = None

    def __post_init__(self):
        if self.at_or_before.lower() not in AT_BEFORE:
            raise InvalidParamsException(
                f"{self.at_or_before} a valid param. Choices: {AT_BEFORE}"
            )
        if (
            (self.timestamp and self.offset)
            or (self.timestamp and self.statement)
            or (self.offset and self.statement)
        ):
            raise InvalidParamsException(f"Please specify only one range parameter.")
        if not self.timestamp and not self.offset and not self.statement:
            raise InvalidParamsException(
                f"Please specify one of the valid range parameters: {RANGE_PARAMS}"
            )

    @property
    def _offset_str(self):
        if self.timestamp:
            return f"timestamp => '{self.timestamp}'"
        elif self.offset:
            return f"offset => {self.offset}"
        elif self.statement:
            return f"statement => '{self.statement}'"

    @property
    def sql(self):
        return f"{self.at_or_before} {self._offset_str};"
