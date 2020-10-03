from dataclasses import dataclass
from typing import Union
from snowday.types.format.base import BaseFormatOptions
from snowday.types.base import Sql
from snowday.types.compression.base import Compression
from snowday.types.compression.auto import AUTO_COMPRESSION


@dataclass
class ParquetFormatOptions(BaseFormatOptions):
    # https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html#syntax
    compression: Compression = AUTO_COMPRESSION
    ignore_utf8_errors: bool = False
    preserve_space: bool = False
    strip_outer_element: bool = False
    disable_snowflake_data: bool = False
    disable_auto_convert: bool = False
    skip_byte_order_mark: bool = True
    trim_space: bool = False
    null_if: str = ""

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=(
                f"compression={self.compression} "
                f"ignore_utf8_errors={self.ignore_utf8_errors} "
                f"preserve_space={self.preserve_space} "
                f"strip_outer_element={self.strip_outer_element} "
                f"disable_snowflake_data={self.disable_snowflake_data} "
                f"disable_auto_convert={self.disable_auto_convert} "
                f"skip_byte_order_mark={self.skip_byte_order_mark} "
                f"trim_space={self.trim_space} "
                f"null_if={self.null_if}"
            )
        )
