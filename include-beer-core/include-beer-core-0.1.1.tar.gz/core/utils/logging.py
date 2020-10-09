#!/usr/bin/env python3

import os
import logging


def load_logger(name, log_file=None, debug=False):
    """Return logger object with handlers set

    Required:
    - name (str): log object
    Optional:
    - log_file (str, None): full path and filename used by FileHandler
    - debug (boolean, False): set level to debug
    """
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    logger = logging.getLogger(name)

    # Set console/stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Set file_handler if log_file supplied
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Set level to debug if true
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return logger
