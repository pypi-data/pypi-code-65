from dataclasses import dataclass
from typing import Union
from snowday.types.base import Sql
from snowday.types.format.base import BaseFormatOptions
from snowday.types.compression.base import Compression
from snowday.types.compression.auto import AUTO_COMPRESSION


@dataclass
class AvroFormatOptions(BaseFormatOptions):
    compression: Compression = AUTO_COMPRESSION
    trim_space: bool = False
    null_if: str = ""

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=(
                f"compression={self.compression.method} "
                f"trim_space={self.trim_space} "
                f"null_if = ({self.null_if})"
            )
        )
