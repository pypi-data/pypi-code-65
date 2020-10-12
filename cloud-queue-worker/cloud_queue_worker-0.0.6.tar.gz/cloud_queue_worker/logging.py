from logging import getLogger, StreamHandler, getLevelName, Formatter
from os import getenv


logger = getLogger("cloud_queue_worker")
logger.setLevel(getLevelName(getenv("LOG_LEVEL", "INFO")))
handler = StreamHandler()
formatter = Formatter(
    fmt="%(name)s [%(asctime)s][%(levelname)s]: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
