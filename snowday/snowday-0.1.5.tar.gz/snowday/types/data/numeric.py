from snowday.types.base import DataType


# Fixed Point
NUMBER = DataType(name="number")  # Up to 38 digits, with optional precision and scale

DECIMAL = DataType(name="decimal")  # Synonymous with NUMBER

NUMERIC = DataType(name="numeric")  # Synonymous with NUMBER

INT = DataType(
    name="int"
)  # Synonymous with NUMBER, except precision and scale cannot be specified

INTEGER = DataType(
    name="integer"
)  # Synonymous with NUMBER, except precision and scale cannot be specified

BIGINT = DataType(
    name="bigint"
)  # Synonymous with NUMBER, except precision and scale cannot be specified

SMALLINT = DataType(
    name="smallint"
)  # Synonymous with NUMBER, except precision and scale cannot be specified

TINYINT = DataType(
    name="tinyint"
)  # Synonymous with NUMBER, except precision and scale cannot be specified

BYTEINT = DataType(
    name="byteint"
)  # Synonymous with NUMBER, except precision and scale cannot be specified


# Floating Point
FLOAT = DataType(name="float")

FLOAT4 = DataType(name="float4")

FLOAT8 = DataType(name="float8")

DOUBLE = DataType(name="double")  # Displayed as FLOAT but stored as DOUBLE

DOUBLE_PRECISION = DataType(
    name="double precision"
)  # Displayed as FLOAT but stored as DOUBLE

REAL = DataType(name="real")  # Displayed as FLOAT but stored as DOUBLE
