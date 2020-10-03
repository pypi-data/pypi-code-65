from dataclasses import dataclass
from typing import Union
from snowday.types.format.base import BaseFormatOptions
from snowday.types.base import Sql
from snowday.types.compression.base import Compression


@dataclass
class CsvFormatOptions(BaseFormatOptions):
    # https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html#syntax
    compression: Compression
    record_delimiter: str = None
    field_delimiter: str = None
    skip_header: int = 0
    skip_blank_lines: bool = False
    date_format: str = "auto"
    time_format: str = "auto"
    timestamp_format: str = "auto"
    binary_format: str = "hex"
    escape: str = None
    escape_unenclosed_field: str = "\\"
    trim_space: bool = False
    field_optionally_enclosed_by: str = None
    null_if: str = None
    error_on_column_count_mismatch: bool = True
    replace_invalid_characters: bool = False
    validate_utf8: bool = True
    empty_field_as_null: bool = True
    skip_byte_order_mark: bool = True  # Unload only
    encoding: Encoding = UTF8_ENCODING

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=(
                f"compression={self.compression.method} "
                f"record_delimiter='{self.record_delimiter}' "
                f""
            )
        )

