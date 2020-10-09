from typing import Dict
from gitkit.Singleton import Singleton
import logging
from logging import Handler, Logger
from enum import IntEnum


class LogLevel(IntEnum):
   NOTSET = 0,
   CRITICAL = 50,
   ERROR = 40,
   WARNING = 30,
   INFO = 20,
   DEBUG = 10


class LogProvider(Singleton):
   """
   docstring
   """

   handler: Handler
   logger: Dict[str, Logger] = {}

# logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s', level=logging.DEBUG)

   def init(self, level: LogLevel = LogLevel.INFO) -> None:

      # Create formatter
      formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s - %(message)s')

      # Initialize handler
      self.handler = logging.StreamHandler()
      self.handler.setLevel(level)
      self.handler.setFormatter(formatter)

   def getLogger(self, name: str, level: LogLevel = LogLevel.INFO) -> Logger:

      name = name.split(".")[-1]
      # if name in self.logger.keys():
      #    return self.logger.get(name)

      # Create logger
      newLogger = logging.getLogger(name)
      newLogger.setLevel(level)
      newLogger.propagate = False
      if self.handler not in newLogger.handlers:
         newLogger.addHandler(self.handler)

      # self.logger[name] = newLogger

      return newLogger
