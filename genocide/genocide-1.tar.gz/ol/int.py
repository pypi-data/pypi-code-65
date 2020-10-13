# OLIB - object library
#
#

import ol
import importlib
import inspect
import pkgutil

def find_cmds(mod):
    cmds = ol.Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                cmds[key] = o
    return cmds

def find_funcs(mod):
    funcs = ol.Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                funcs[key] = "%s.%s" % (o.__module__, o.__name__)
    return funcs

def find_mods(mod):
    mods = ol.Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                mods[key] = o.__module__
    return mods

def find_classes(mod):
    nms = ol.Ol()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, ol.Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            nms.append(o.__name__, t)
    return nms

def find_class(mod):
    mds = ol.Ol()
    for key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, ol.Object):
            mds.append(o.__name__, o.__module__)
    return mds

def find_names(mod):
    tps = ol.Ol()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, ol.Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            tps.append(o.__name__.lower(), t)
    return tps

def walk(names):
    for name in names.split(","):
        spec = importlib.util.find_spec(name)
        if not spec:
            continue
        pkg = importlib.util.module_from_spec(spec)
        pn = getattr(pkg, "__path__", None)
        if not pn:
            continue
        for mi in pkgutil.iter_modules(pn):
            mn = "%s.%s" % (name, mi.name)
            mod = ol.utl.direct(mn)
            ol.tbl.cmds.update(vars(find_cmds(mod)))
            ol.tbl.funcs.update(vars(find_funcs(mod)))
            ol.tbl.mods.update(vars(find_mods(mod)))
            ol.tbl.names.update(vars(find_names(mod)))
            ol.tbl.classes.update(vars(find_class(mod)))
