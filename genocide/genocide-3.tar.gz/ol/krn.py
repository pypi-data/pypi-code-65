# OLIB - object library
#
#

import importlib
import ol
import os
import pkgutil
import sys
import time
import threading

booted = False
starttime = time.time()

class Kernel(ol.hdl.Handler, ol.ldr.Loader):

    classes = ol.Object()
    cmds = ol.Object()
    funcs = ol.Object()
    mods = ol.Object()
    names = ol.Object()

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

    def direct(self, txt):
        print(txt.rstrip())

    def init(self, mns, exc=""):
        if not mns:
            return
        exclude = exc.split(",")
        for mn in ol.utl.spl(mns):
            if mn in exclude:
                continue
            if mn not in self.table:
                self.load(mn)
            if mn in self.table:
                func = getattr(self.table[mn], "init", None)
                if func:
                    ol.tsk.launch(func, self, name=ol.get_name(func))

    def put(self, e):
        self.queue.put_nowait(e)

    def say(self, channel, txt):
        self.direct(txt)

    def start(self):
        assert ol.wd
        super().start()

    def stop(self):
        self.stopped = True
        self.queue.put(None)

    def wait(self):
        while not self.stopped:
            time.sleep(60.0)

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
                mod = ol.utl.direct(mn)
                ol.update(self.cmds, vars(ol.int.find_cmds(mod)))
                ol.update(self.funcs, vars(ol.int.find_funcs(mod)))
                ol.update(self.mods, vars(ol.int.find_mods(mod)))
                ol.update(self.names, vars(ol.int.find_names(mod)))
                ol.update(self.classes, vars(ol.int.find_class(mod)))

kernels = []

def boot(name, wd, md=""):
    cfg = ol.prs.parse_cli()
    k = get_kernel()
    ol.update(k.cfg, cfg)
    ol.wd = k.cfg.wd = wd
    k.cfg.md = md or os.path.join(ol.wd, "gmod", "")
    if "b" in k.cfg.opts:
        print("%s started at %s" % (name.upper(), time.ctime(time.time()))) 
        print(ol.format(k.cfg))
    return k

def cmd(txt, wd=None):
    if not txt:
        return 
    global booted
    if not booted:
        k = boot("genocide", wd or os.path.expanduser("~/.genocide"))
        booted = True
    else:
        k = get_kernel()
    ol.bus.bus.add(k)
    if ol.utl.root():
        scandir(os.path.join(k.cfg.wd, "gmod"), "gmod")
    e = ol.evt.Event()
    e.txt = txt
    k.dispatch(e)
    return e

def get_kernel():
    if kernels:
        return kernels[0]
    return Kernel()

def scandir(path, modname="ol"):
    k = get_kernel()
    mods = []
    ol.utl.cdir(path + os.sep + "")
    sys.path.insert(0, path)
    for fn in os.listdir(path):
        if fn.startswith("_") or not fn.endswith(".py"):
            continue
        mn = "%s.%s" % (modname, fn[:-3])
        try:
            module = k.load(mn)
        except Exception as ex:
            print(ol.utl.get_exception())
            continue
        mods.append(module)
    return mods
