import logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """
    log
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
