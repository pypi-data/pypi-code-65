# -*- coding: utf-8 -*-

import sys

from .cmd.argument import Argument
from .cmd.banner import BANNER
from .config.config import Config, ConfigException
from .logger.logger import Logger
from .scheduler.scheduler import Scheduler, SchedulerException


def main():
    print(BANNER)

    argument = Argument()
    arg = argument.parse(sys.argv)

    try:
        config = Config()
        config.pg_host = arg.pg_address.split(":")[0]
        config.pg_port = arg.pg_address.split(":")[1]
        config.pg_user = arg.pg_login.split("/")[0]
        config.pg_pass = arg.pg_login.split("/")[1]
        config.redis_host = arg.redis_address.split(":")[0]
        config.redis_port = arg.redis_address.split(":")[1]
        config.redis_pass = arg.redis_pass
        config.repo_count = arg.repo_count
        config.repo_host = arg.repo_host.split(",")
        config.repo_lang = arg.repo_lang.split(",")
    except ConfigException as e:
        Logger.error(str(e))
        return -1

    try:
        scheduler = Scheduler(config)
        scheduler.run()
    except SchedulerException as e:
        Logger.error(str(e))
        return -2

    return 0
