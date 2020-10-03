from snowday.types.data.datetime import (
    DATE,
    TIME,
    TIMESTAMP_LTZ,
    TIMESTAMP_NTZ,
    TIMESTAMP_TZ,
    DATETIME,
    TIMESTAMP,
)
from snowday.types.data.geography import GEOGRAPHY
from snowday.types.data.logical import BOOLEAN
from snowday.types.data.numeric import (
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
)
from snowday.types.data.semistruct import (
    OBJECT,
    VARIANT,
    ARRAY,
)
from snowday.types.data.string import (
    VARCHAR,
    CHAR,
    CHARACTER,
    STRING,
    TEXT,
    BINARY,
    VARBINARY,
)


ALL_TYPES = [
    # Time
    DATE,
    TIME,
    TIMESTAMP_LTZ,
    TIMESTAMP_NTZ,
    TIMESTAMP_TZ,
    DATETIME,
    TIMESTAMP,
    # Geo
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
    OBJECT,
    VARIANT,
    ARRAY,
    # String
    VARCHAR,
    CHAR,
    CHARACTER,
    STRING,
    TEXT,
    BINARY,
    VARBINARY,
]
