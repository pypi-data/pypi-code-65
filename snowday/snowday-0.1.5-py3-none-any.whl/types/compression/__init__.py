from snowday.types.compression.base import Compression, NO_COMPRESSION
from snowday.types.compression.auto import AUTO_COMPRESSION
from snowday.types.compression.gzip import GZIP_COMPRESSION
from snowday.types.compression.bz2 import BZ2_COMPRESSION
from snowday.types.compression.brotli import BROTLI_COMPRESSION
from snowday.types.compression.zstd import ZSTD_COMPRESSION
from snowday.types.compression.deflate import DEFLATE_COMPRESSION
from snowday.types.compression.raw_deflate import RAW_DEFLATE_COMPRESSION
from snowday.types.compression.snappy import SNAPPY_COMPRESSION


ALL_COMPRESSION_TYPES = [
    AUTO_COMPRESSION,
    GZIP_COMPRESSION,
    BZ2_COMPRESSION,
    BROTLI_COMPRESSION,
    ZSTD_COMPRESSION,
    DEFLATE_COMPRESSION,
    RAW_DEFLATE_COMPRESSION,
    NO_COMPRESSION,
    SNAPPY_COMPRESSION,
]
