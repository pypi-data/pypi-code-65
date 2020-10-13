
import logging
import time

def init_logger(filepath, verbosity=1, name=None):

    """
    :log effect:
        [2019-12-19 13:56:52,338][train.py][line:3][INFO] start training!
        [2019-12-19 13:57:52,338][train.py][line:8][INFO] Epoch:[1/10] loss=... acc=...
        [2019-12-19 13:58:52,338][train.py][line:8][INFO] Epoch:[2/10] loss=... acc=...


    :param filepath:  the fold of log file
    :param verbosity:
    :param name:
    :return:
    """

    level_dict = {0: logging.DEBUG, 1: logging.INFO, 2: logging.WARNING}
    formatter = logging.Formatter(
        "[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s] %(message)s"
    )
    logger = logging.getLogger(name)
    logger.setLevel(level_dict[verbosity])
    time_str = time.strftime('%Y_%m_%d_%H_%M_%S')
    filename = '{}/exp_{}.log'.format(filepath,time_str)

    fh = logging.FileHandler(filename, "w")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger