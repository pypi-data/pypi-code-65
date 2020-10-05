# OLIB - object library
#
#

__version__ = 11

import importlib
import ol
import os
import sys
import time
import threading

starttime = time.time()

class Kernel(ol.hdl.Handler):

    def __init__(self):
        super().__init__()
        self.ready = threading.Event()
        self.stopped = False
        self.cfg = ol.Cfg()
        kernels.append(self)

    def announce(self, txt):
        pass

    def cmd(self, txt):
        if not txt:
            return None
        e = ol.hdl.Event()
        e.txt = txt
        ol.bus.bus.add(self)
        self.dispatch(e)
        return e

    def init(self, mns):
        if not mns:
            return
        for mn in ol.utl.spl(mns):
            if mn in self.table:
                func = getattr(self.table[mn], "init", None)
                if func:
                    ol.tsk.launch(func, self, name=ol.get_name(func))

    def scandir(self, path, modname="ol"):
        mods = []
        ol.utl.cdir(path + os.sep + "")
        sys.path.insert(0, path)
        for fn in os.listdir(path):
            if fn.startswith("_") or not fn.endswith(".py"):
                continue
            mn = "%s.%s" % (modname, fn[:-3])
            try:
                module = self.load(mn)
            except Exception as ex:
                print(ol.utl.get_exception())
                continue
            mods.append(module)
        return mods

    def say(self, channel, txt):
        print(txt)

    def start(self):
        assert ol.wd
        super().start()

    def stop(self):
        self.stopped = True
        self.queue.put(None)

    def wait(self):
        while not self.stopped:
            time.sleep(60.0)

kernels = []

def boot(name, wd, md=""):
    cfg = ol.prs.parse_cli()
    k = get_kernel()
    ol.update(k.cfg, cfg)
    ol.wd = k.cfg.wd = wd
    k.cfg.md = md or os.path.join(ol.wd, "bmod", "")
    if "b" in k.cfg.opts:
        print("%s started at %s" % (name.upper(), time.ctime(time.time()))) 
        print(ol.format(k.cfg))
    return k

def get_kernel():
    if kernels:
        return kernels[0]
    return Kernel()
