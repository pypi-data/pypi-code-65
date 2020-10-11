import logging
from pathlib import Path

def get_logger() -> logging.Logger:
    """
    Get a logger.

    Returns
    -------
    logger: Logger.
    """
    logger = logging.getLogger("wendigo")
    
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    return logger

Logger = get_logger()