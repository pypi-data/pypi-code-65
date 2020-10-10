# -*- coding: utf-8 -*-
import pytest

from zwutils.sysutils import *

def test_proc():
    r = pids_by_name()
    assert len(r)>0

    r = pids_by_name('mongod')
    assert len(r) == 1

    r = pids_by_name(r'mongo.*')
    assert len(r) == 1

def test_run_shell():
    r = run_shell('dir', 'd:\\')
    assert len(r) != 0