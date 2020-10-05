# BOTLIB - framework to program bots
#
#

import importlib
import inspect
import ol
import pkgutil

class Loader(ol.Object):

    def __init__(self):
        super().__init__()
        self.cmds = ol.Object()
        self.names = ol.Ol()
        self.table = ol.Object()
        self.types = ol.Object()

    def load(self, name):
        if name not in self.table:
            self.table[name] = importlib.import_module(name)

    def scan(self, mod):
        ol.update(self.cmds, find_cmds(mod))
        ol.update(self.names, find_names(mod))
        ol.update(self.types, find_types(mod))

    def walk(self, names):
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
                self.load(mn)
                self.scan(self.table[mn])

def find_cmds(mod):
    cmds = {}
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                cmds[key] = o
    return cmds

def find_names(mod):
    tps = ol.Ol()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, ol.Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            tps.append(o.__name__.lower(), t)
    return tps

def find_types(mod):
    tps = ol.Object()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, ol.Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            tps[o.__name__.lower()] = t
    return tps
