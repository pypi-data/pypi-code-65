# OLIB - object library
#
#

import importlib
import ol
import pkgutil
import queue
import sys
import threading
import _thread

dispatchlock = _thread.allocate_lock()

class Handler(ol.Object):

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.stopped = False

    def dispatch(self, e):
        e.parse()
        if not e.orig:
            e.orig = repr(self)
        func = self.get_cmd(e.cmd)
        if not func:
            mn = ol.get(ol.tbl.mods, e.cmd, None)
            if mn:
                self.load(mn)
                func = self.get_cmd(e.cmd)
        if func:
            try:
                func(e)
                e.show()
            except Exception as ex:
                print(ol.utl.get_exception())
        e.ready.set()

    def get_cmd(self, cmd):
        mn = ol.get(ol.tbl.mods, cmd, None)
        if not mn:
             return
        if mn in sys.modules:
            mod = sys.modules[mn]
        else:
            mod = ol.utl.direct(mn)
        if mod:
            return getattr(mod, cmd, None)

    def handler(self):
        while not self.stopped:
            event = self.queue.get()
            if not event:
                break
            if "orig" not in event:
                event.orig = repr(self)
            if event.txt:
                if self.cfg.nothread:
                    self.dispatch(event)
                else:
                    ol.tsk.launch(self.dispatch, event)
            else:
                event.ready.set()

    def put(self, e):
        self.queue.put_nowait(e)

    def start(self):
        ol.tsk.launch(self.handler)

    def stop(self):
        self.stopped = True
        self.queue.put(None)
