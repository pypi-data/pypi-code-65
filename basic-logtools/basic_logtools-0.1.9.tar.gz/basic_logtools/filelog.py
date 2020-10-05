import os
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import timezone


class LogFile:
    _logger_methods = ('debug', 'error', 'info', 'warning', 'critical',
                       'exception')
    LOG_LEVELS = {
        'CRITICAL': 50,
        'ERROR': 40,
        'WARNING': 30,
        'INFO': 10,
        'NOTSET': 0
    }

    def __init__(self,
                 class_name,
                 code,
                 hostname,
                 path='./',
                 max_bytes=10240,
                 backup_count=18,
                 base_level='INFO'):
        """
        params:

        clasname :: nombre de clase que lo ejecuta
        code :: codigo activo
        path :: ruta donde almacenará log
        """
        self.class_name = class_name
        self.hostname = hostname
        self.code = code
        self.init_datetime = datetime.now(timezone.utc).isoformat()
        self.logpath = Path(path)
        self.logpath.mkdir(parents=True, exist_ok=True)
        # create log instance
        logger = logging.getLogger("%s_%s" % (class_name, code))
        handler = RotatingFileHandler(self.file_path,
                                      mode='w',
                                      maxBytes=max_bytes,
                                      backupCount=backup_count)
        formatter = logging.Formatter(
            fmt=
            '%(asctime)s %(levelname)s  %(process)d %(pathname)s %(filename)s %(module)s %(funcName)s %(message)s'
        )
        LOG_LEVEL = self.LOG_LEVELS.get(base_level, 0)
        handler.setLevel(LOG_LEVEL)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
        self.__logger = logger
        self.__handler = handler

    @property
    def file_name(self):
        return "%s_%s_%s_%s.log" % (self.class_name, self.hostname, self.code,
                                    self.init_datetime)

    @property
    def logger(self):
        return self.__logger

    @property
    def handler(self):
        return self.__handler

    def __getattr__(self, name):
        if name in LogFile._logger_methods:
            return getattr(self.__logger, name)

    def save(self, level, msg, *args, **kwargs):
        self.__logger.log(level, msg, *args, **kwargs)

    @property
    def file_path(self):
        return '%s/%s' % (self.logpath, self.file_name)

    def close(self):
        self.__handler.close()
