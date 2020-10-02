# -*- coding: utf-8 -*-


class SchedulerException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Scheduler(object):
    def __init__(self, config=None):
        if config is None:
            raise SchedulerException("config invalid")

    def run(self):
        # TODO
        pass
