import logging

from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger, console_handler, formatter


def setup_file_logging(cfg, logger, formatter, console_handler):
    try:
        logger.setLevel(cfg["log_level"])

        if cfg["log_file_location"]:
            filehandler = TimedRotatingFileHandler(cfg["log_file_location"], when="d", interval=1, backupCount=7)
            filehandler.setFormatter(formatter)
            logger.addHandler(filehandler)
            logger.removeHandler(console_handler)
        return logger
    # todo: catch explicit
    except Exception:
        raise
