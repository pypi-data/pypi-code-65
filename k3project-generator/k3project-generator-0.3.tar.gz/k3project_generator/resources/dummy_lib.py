"""
Put module description here


"""

import logging

logger = logging.getLogger(__name__)

def do_something(postionalArg):
    logger.debug("This is a debug message")
    logger.info("This is a info message")
    logger.warning("This is a warning message")
    logger.error("This is a error message")
    print(f"Positional argument was {postionalArg}")
    return "a_result"