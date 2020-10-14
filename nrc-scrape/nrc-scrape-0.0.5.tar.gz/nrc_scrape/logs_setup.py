import logging
import os

logs = ["success_log", "error_log", "fof_log", "op_log"]

if not os.path.exists("logs"):
    os.mkdir("logs")

for log in logs:

    logger = logging.getLogger(log)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(f"./logs/{log}.log")
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

sl = logging.getLogger("success_log")
el = logging.getLogger("error_log")
fl = logging.getLogger("fof_log")
ol = logging.getLogger("op_log")
