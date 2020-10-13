
import logging


class Logger(object):

    """
    This class representing the Logger level and log file path.
    """

    def __init__(self, level, file_path):
        self.level = level
        self.file_path = file_path

    @staticmethod
    def get_instance(level, file_path):

        """
        Creates an Logger class instance with the specified log level and file path.
        :param level: A Levels class instance containing the log level.
        :param file_path: A str containing the log file path.
        :return: A Logger class instance.
        """

        return Logger(level=level, file_path=file_path)

    import enum

    class Levels(enum.Enum):

        """
        This enum used to give logger levels.
        """

        CRITICAL = logging.CRITICAL
        ERROR = logging.ERROR
        WARNING = logging.WARNING
        INFO = logging.INFO
        DEBUG = logging.DEBUG
        NOTSET = logging.NOTSET


class SDKLogger(object):

    """
    This class to initialize the SDK logger.
    """

    def __init__(self, level, file_path):

        logger = logging.getLogger('SDKLogger')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(filename)s - %(funcName)s - %(lineno)d  - %(message)s')
        console_handler = logging.StreamHandler()
        logger.setLevel(level.name)

        if file_path is not None:
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(level.name)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        else:
            console_handler.setLevel(level.name)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    @staticmethod
    def initialize(level, file_path):
        SDKLogger(level=level, file_path=file_path)
