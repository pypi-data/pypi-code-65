from datetime import date, datetime
from dataclasses import dataclass, field
import json
from typing import List, Union
from snowday.objects.base_schema import SchemaObject
from snowday.exceptions import (
    InvalidWhitespaceException,
    InvalidColumnConstraintException,
)
from snowday.types.base import Sql
from snowday.types import (
    # Datetime
    DATE,
    TIME,
    TIMESTAMP_LTZ,
    TIMESTAMP_NTZ,
    TIMESTAMP_TZ,
    DATETIME,
    TIMESTAMP,
    # Geography
    GEOGRAPHY,
    # Logical
    BOOLEAN,
    # Numeric
    NUMBER,
    DECIMAL,
    NUMERIC,
    INT,
    INTEGER,
    BIGINT,
    SMALLINT,
    TINYINT,
    BYTEINT,
    FLOAT,
    FLOAT4,
    FLOAT8,
    DOUBLE,
    DOUBLE_PRECISION,
    REAL,
    # Semistruct
    VARIANT,
    OBJECT,
    ARRAY,
    # String
    VARCHAR,
    CHAR,
    CHARACTER,
    STRING,
    TEXT,
    BINARY,
    VARBINARY,
)


def get_default_sql(obj) -> str:
    if hasattr(obj, "default"):
        if obj.default == False:  # Has to be first because... false is falsey
            return f" default {obj.default}"
        if obj.default:  # But `None` should be politely excused
            if obj.datatype in ["varchar", "char", "string", "text"]:
                return f" default '{obj.default}'"
            elif obj.datatype == "boolean":
                return f" default {obj.default}"
            elif obj.datatype == "date":
                return f" default cast('{obj.default}' as date)"
            elif obj.datatype in ["datetime", "timestamp", "timestamp_ntz"]:
                return f" default cast('{obj.default}' as timestamp_ntz(9))"
            elif obj.datatype == "time":
                return f" default cast('{obj.default}' as time(9))"
            elif obj.datatype == "timestamp_ltz":
                return f" default cast('{obj.default}' as timestamp_ltz(9))"
            elif obj.datatype == "timestamp_tz":
                return f" default cast('{obj.default}' as timestamp_tz(9))"
            elif obj.datatype == "variant":
                return f" default parse_json('{json.dumps(obj.default)}')"
            elif obj.datatype == "object":
                return f" default parse_json('{json.dumps(obj.default)}')"
            elif obj.datatype == "array":
                return f" default parse_json('{json.dumps(obj.default)}')"
            return f" default {obj.default}"
    return ""


@dataclass
class Column:
    """A base class for abstracting up sql consistencies.
    """

    name: str
    comment: str = None
    # inline constraints
    unique: bool = False
    not_null: bool = False
    # foreign_key: Column  # FIXME! do this!

    def __post_init__(self):
        # Make sure columns don't have whitespace.
        if " " in self.name:
            msg = f"Column names cannot have whitespace. Please change column name {self.name} to {self.name.replace(' ', '_')} or equivalent."
            raise InvalidWhitespaceException(msg)
        # Ensure names are uppercased.
        self.name = self.name.upper()
        # Make sure columns don't have both a unique constraint and a column default.
        if hasattr(self, "default"):
            if self.default and self.unique:
                raise InvalidColumnConstraintException(
                    "A column cannot have both a default and a unique constraint. Please alter one or the other."
                )

    @property
    def datatype(self):
        return "column"

    @property
    def datatype_modifier(self):
        return ""

    @property
    def unique_sql(self):
        if self.unique:
            return " unique"
        return ""

    @property
    def not_null_sql(self):
        if self.not_null:
            return " not null"
        return ""

    @property
    def collation_sql(self):
        # FIXME! Incorporate this functionality
        return ""

    # @property
    # def primary_key_sql(self): # FIXME! do this!
    #     if self.primary_key:
    #         return " primary key "
    #     return ""

    # @property
    # def foreign_key_sql(self): # FIXME! do this!
    #     if self.foreign_key

    @property
    def default_sql(self):
        return get_default_sql(self)

    @property
    def comment_sql(self):
        if self.comment:
            return f" comment '{self.comment}'"
        return ""

    @property
    def sql(self):
        return Sql(
            statement=(
                f"{self.name} {self.datatype.name}{self.datatype_modifier}"
                f"{self.collation_sql}{self.default_sql}"
                f"{self.not_null_sql}{self.unique_sql}{self.comment_sql}"
            )
        )


@dataclass
class BaseNumberColumn(Column):
    default: float = None
    precision: int = 38
    scale: int = 0

    @property
    def datatype(self):
        return NUMBER

    @property
    def datatype_modifier(self):
        return f"({self.precision}, {self.scale})"


@dataclass
class BaseIntColumn(Column):
    default: int = None

    @property
    def datatype(self):
        return INTEGER


@dataclass
class BaseFloatingPointColumn(Column):
    default: float = None

    @property
    def datatype(self):
        return FLOAT


@dataclass
class BaseTextColumn(Column):
    default: str = None

    @property
    def datatype(self):
        return TEXT


@dataclass
class BaseDateColumn(Column):
    default: date = None

    @property
    def datatype(self):
        return DATE


@dataclass
class BaseDatetimeColumn(Column):
    default: datetime = None

    @property
    def datatype(self):
        return DATETIME


# Numeric Columns


@dataclass
class NumberColumn(BaseNumberColumn):
    default: float = None

    @property
    def datatype(self):
        return NUMBER


@dataclass
class DecimalColumn(BaseNumberColumn):
    default: float = None

    @property
    def datatype(self):
        return DECIMAL


@dataclass
class NumericColumn(BaseNumberColumn):
    default: float = None

    @property
    def datatype(self):
        return NUMERIC


# Fixed precision/scale


@dataclass
class IntColumn(BaseIntColumn):
    @property
    def datatype(self):
        return INT


@dataclass
class BigIntColumn(BaseIntColumn):
    @property
    def datatype(self):
        return BIGINT


@dataclass
class SmallIntColumn(BaseIntColumn):
    @property
    def datatype(self):
        return SMALLINT


@dataclass
class TinyIntColumn(BaseIntColumn):
    @property
    def datatype(self):
        return TINYINT


@dataclass
class ByteIntColumn(BaseIntColumn):
    @property
    def datatype(self):
        return BYTEINT


@dataclass
class FloatColumn(BaseFloatingPointColumn):
    @property
    def datatype(self):
        return FLOAT


@dataclass
class Float4Column(BaseFloatingPointColumn):
    @property
    def datatype(self):
        return FLOAT4


@dataclass
class Float8Column(BaseFloatingPointColumn):
    @property
    def datatype(self):
        return FLOAT8


@dataclass
class DoubleColumn(BaseFloatingPointColumn):
    @property
    def datatype(self):
        return DOUBLE


@dataclass
class RealColumn(BaseFloatingPointColumn):
    @property
    def datatype(self):
        return REAL


# Text Columns


@dataclass
class VarcharColumn(BaseTextColumn):
    length: int = 16777216

    @property
    def datatype(self):
        return VARCHAR

    @property
    def datatype_modifier(self):
        return f"({self.length})"


@dataclass
class CharColumn(BaseTextColumn):
    @property
    def datatype(self):
        return CHAR


@dataclass
class StringColumn(BaseTextColumn):
    length: int = 16777216

    @property
    def datatype(self):
        return STRING

    @property
    def datatype_modifier(self):
        return f"({self.length})"


@dataclass
class TextColumn(BaseTextColumn):
    length: int = 16777216

    @property
    def datatype(self):
        return TEXT

    @property
    def datatype_modifier(self):
        return f"({self.length})"


@dataclass
class BinaryColumn(BaseTextColumn):
    @property
    def datatype(self):
        return BINARY


@dataclass
class VarbinaryColumn(BaseTextColumn):
    @property
    def datatype(self):
        return VARBINARY


# Logical Columns
@dataclass
class BooleanColumn(Column):
    default: bool = None

    @property
    def datatype(self):
        return BOOLEAN


# Date & Time Columns
@dataclass
class DateColumn(BaseDateColumn):
    @property
    def datatype(self):
        return DATE


@dataclass
class DatetimeColumn(BaseDatetimeColumn):
    @property
    def datatype(self):
        return DATETIME


@dataclass
class TimeColumn(BaseDatetimeColumn):
    @property
    def datatype(self):
        return TIME


@dataclass
class TimestampColumn(BaseDatetimeColumn):
    @property
    def datatype(self):
        return TIMESTAMP


@dataclass
class TimestampLTZColumn(BaseDatetimeColumn):
    @property
    def datatype(self):
        return TIMESTAMP_LTZ


@dataclass
class TimestampNTZColumn(BaseDatetimeColumn):
    @property
    def datatype(self):
        return TIMESTAMP_NTZ


@dataclass
class TimestampTZColumn(BaseDatetimeColumn):
    @property
    def datatype(self):
        return TIMESTAMP_TZ


# Semi-structured Columns
@dataclass
class VariantColumn(Column):
    default: Union[list, dict] = None

    @property
    def datatype(self):
        return VARIANT


@dataclass
class ObjectColumn(Column):
    default: dict = None

    @property
    def datatype(self):
        return OBJECT


@dataclass
class ArrayColumn(Column):
    default: list = None

    @property
    def datatype(self):
        return ARRAY


# Geospatial Columns
@dataclass
class GeographyColumn(Column):
    default: Union[
        dict, str
    ] = None  # FIXME: string must be in WKT, WKB, EWKT, EWKB format

    @property
    def datatype(self):
        return GEOGRAPHY


ACCEPTED_TABLE_COLUMNS = Union[
    NumberColumn,
    IntColumn,
    BigIntColumn,
    SmallIntColumn,
    TinyIntColumn,
    ByteIntColumn,
    FloatColumn,
    Float4Column,
    Float8Column,
    DoubleColumn,
    RealColumn,
    VarcharColumn,
    CharColumn,
    StringColumn,
    TextColumn,
    BooleanColumn,
    DateColumn,
    DatetimeColumn,
    TimeColumn,
    TimestampColumn,
    TimestampLTZColumn,
    TimestampNTZColumn,
    TimestampTZColumn,
    VariantColumn,
    ObjectColumn,
    ArrayColumn,
    GeographyColumn,
]


@dataclass
class Table(SchemaObject):
    columns: List[ACCEPTED_TABLE_COLUMNS] = None
    cluster_keys: List[ACCEPTED_TABLE_COLUMNS] = None
    # FIXME! Do something useful with cluster keys.

    def __post_init__(self):
        for column in self.columns:
            setattr(self, f"_{column.name}", column)

    @property
    def resource_type(self):
        return "table"

    @property
    def _definition_sql(self):
        col_sql = ", ".join(c.sql for c in self.columns)
        return f"({col_sql})"

    @property
    def create(self):
        return f"create {self.resource_type} {self.fqn} {self._definition_sql};"

    @property
    def create_if_not_exists(self):
        return f"create {self.resource_type} if not exists {self.fqn} {self._definition_sql};"

    @property
    def create_or_replace(self):
        return (
            f"create or replace {self.resource_type} {self.fqn} {self._definition_sql};"
        )


@dataclass
class ExternalTable:
    # FIXME! Do this!
    pass
