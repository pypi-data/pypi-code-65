# OLIB - object library
#
#

import importlib
import inspect
import ol
import pkgutil

class Loader(ol.Object):

    classes = ol.Object()
    cmds = ol.Object()
    funcs = ol.Object()
    mods = ol.Object()
    names = ol.Object()
    table = ol.Object()

    def load(self, name):
        if name not in self.table:
            self.table[name] = importlib.import_module(name)
        return self.table[name]

