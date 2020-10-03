from dataclasses import dataclass
from typing import Union
from snowday.types.format.base import BaseFormatOptions
from snowday.types.base import Sql
from snowday.types.compression.base import Compression


@dataclass
class JsonFormatOptions(BaseFormatOptions):
    compression: Compression
    date_format: str = None
    time_format: str = None
    timestamp_format: str = None
    binary_format: str = None
    trim_space: bool = False
    null_if: str = ""
    file_extension: str = None  # UNLOAD only
    enable_octal: bool = False
    allow_duplicate: bool = False
    strip_outer_array: bool = False
    strip_null_values: bool = False
    ignore_utf8_errors: bool = False
    skip_byte_order_mark: bool = True

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=(
                f"compression={self.compression.method} "
                f"date_format='{self.date_format}' "  # FIXME! Need to wrap in single quotes or AUTO
                f"time_format='{self.time_format}' "  # FIXME! Need to wrap in single quotes or AUTO
                f"timestamp_format='{self.timestamp_format}' "  # FIXME! Need to wrap in single quotes or AUTO
                f"binary_format={self.binary_format} "
                f"trim_space={self.trim_space} "
                f"null_if=({self.null_if}) "
                f"file_extension='{self.file_extension}' "
                f"enable_octal={self.enable_octal} "
                f"allow_duplicate={self.allow_duplicate} "
                f"strip_outer_array={self.strip_outer_array} "
                f"strip_null_values={self.strip_null_values} "
                f"ignore_utf8_errors={self.ignore_utf8_errors} "
                f"skip_byte_order_mark={self.skip_byte_order_mark}"
            )
        )
