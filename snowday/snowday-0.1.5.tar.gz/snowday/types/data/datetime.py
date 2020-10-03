from snowday.types.base import DataType

DATE = DataType(name="date")  # No time elements
TIME = DataType(name="time")  # HH:MI:SS

TIMESTAMP_LTZ = DataType(
    name="timestamp_ltz"
)  # UTC time with specified precision; operations performed in current session's tz
TIMESTAMP_NTZ = DataType(
    name="timestamp_ntz"
)  # Wallclock time with specified precision; operations performed without taking any tz into account
TIMESTAMP_TZ = DataType(
    name="timestamp_tz"
)  # UTC time with associated tz offset; session tz offset of no offset is provided


# Aliases
DATETIME = DataType(name="datetime")  # Alias of TIMESTAMP_LTZ
TIMESTAMP = DataType(
    name="timestamp"
)  # User-specific alias via TIMESTAMP_TYPE_MAPPING session param; TIMESTAMP_NTZ by default
