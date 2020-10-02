import logging
logger = logging.getLogger("vessel-cli")
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
