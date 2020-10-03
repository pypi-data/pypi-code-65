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
    # snappy_compression: bool NOTE! This has been deprecated.
    binary_as_text: bool
    trim_space: bool
    null_if: str

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=(
                f"compression={self.compression.method} "
                f"binary_as_text={self.binary_as_text} "
                f"trim_space={self.trim_space} "
                f"null_if=({self.null_if})"
            )
        )
