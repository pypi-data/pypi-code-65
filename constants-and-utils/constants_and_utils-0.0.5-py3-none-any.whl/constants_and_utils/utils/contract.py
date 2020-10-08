import abc


class LoggingInterface:
    """Contract for logging.

    Attributes:
        debug_on (bool): Debug status, default `False`.
    """
    debug_on = False

    @abc.abstractmethod
    def debug(self, msg: str):
        pass

    @abc.abstractmethod
    def info(self, msg: str):
        pass

    @abc.abstractmethod
    def error(self, msg: str):
        pass
