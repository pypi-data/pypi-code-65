from abc import ABC
from logging import Logger, getLogger

class Logging(ABC):
    __logger: Logger = None
    logger_name: str
    
    def __init__(self):
        self.init_logger()
    
    @property
    def logger(self) -> Logger:
        if (self.__logger is None):
            self.init_logger()
        return self.__logger
    
    def init_logger(self):
        if (getattr(self, 'logger_name', None) is None):
            # Guard against frozen classes
            object.__setattr__(self, 'logger_name', self.__module__.replace('_', '-'))
        
        object.__setattr__(self, f'_{Logging.__name__}__logger', getLogger(self.logger_name))

__all__ = \
[
    'Logging',
]
