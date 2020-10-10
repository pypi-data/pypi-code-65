# -*- coding: utf-8 -*-

import os
import sys
import typing


def _daemon(pids):

    while pids:
        pid, _ = os.wait()
        pids.remove(pid)


def fork_processes(number: int, daemon: typing.Callable = _daemon):

    pids = set()

    for num in range(number):

        pid = os.fork()

        if pid == 0:
            return num
        else:
            pids.add(pid)

    daemon(pids)

    sys.exit(0)
