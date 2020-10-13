# OLIB - object library
#
#

import importlib
import inspect
import os
import sys
import threading
import traceback

class ENOCLASS(Exception):

    pass

def cdir(path):
    if os.path.exists(path):
        return
    res = ""
    path2, _fn = os.path.split(path)
    for p in path2.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
            os.chmod(padje, 0o700)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass

def direct(name):
    return importlib.import_module(name)

def get_cls(name):
    try:
        modname, clsname = name.rsplit(".", 1)
    except:
        raise ENOCLASS(name)
    if modname in sys.modules:
        mod = sys.modules[modname]
    else:
        mod = importlib.import_module(modname)
    return getattr(mod, clsname)

def find_modules(pkgs, skip=None):
    modules = []
    for pkg in pkgs.split(","):
        if skip is not None and skip not in pkg:
            continue
        try:
            p = direct(pkg)
        except ModuleNotFoundError:
            continue
        for _key, m in inspect.getmembers(p, inspect.ismodule):
            if m not in modules:
                modules.append(m)
    return modules

def get_exception(txt="", sep=" "):
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = []
    for elem in trace:
        if elem[0].endswith(".py"):
            plugfile = elem[0][:-3].split(os.sep)
        else:
            plugfile = elem[0].split(os.sep)
        mod = []
        for element in plugfile[::-1]:
            mod.append(element)
            if "ol" in element or "gmod" in element or "genocide" in element:
                break
        ownname = ".".join(mod[::-1])
        result.append("%s:%s" % (ownname, elem[1]))
    res = "%s %s: %s %s" % (sep.join(result), exctype, excvalue, str(txt))
    del trace
    return res

def list_files(wd):
    path = os.path.join(wd, "store")
    if not os.path.exists(path):
        return ""
    return " ".join(os.listdir(path))

def privileges(name):
    if os.getuid() != 0:
        return
    pwnam = pwd.getpwnam(name)
    os.setgroups([])
    os.setgid(pwnam.pw_gid)
    os.setuid(pwnam.pw_uid)
    old_umask = os.umask(0o22)

def root():
    if os.geteuid() != 0:
        return False
    return True

def spl(txt):
    return iter([x for x in txt.split(",") if x])

def touch(fname):
    try:
        fd = os.open(fname, os.O_RDWR | os.O_CREAT)
        os.close(fd)
    except (IsADirectoryError, TypeError):
        pass
