import os
import sys
from loguru import logger


STDOUT_SINK = {"sink": sys.stdout, "level": "DEBUG"}
FILE_SINK = {
    "sink": "snowday.log",
    "rotation": "1 MB",
    "retention": "1 day",
    "enqueue": True,
    "backtrace": True,
    "compression": "gz",
}

CONFIG = {"handlers": [STDOUT_SINK, FILE_SINK], "extra": {"pkg": "[snowday]"}}


def get_logger(config=CONFIG):
    l = logger
    l.configure(**config)
    return l
