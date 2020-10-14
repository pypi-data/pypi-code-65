# OLIB - object library
#
#

import atexit
import ol
import readline
import threading

def __dir__():
    return ("Console", "getcompleter", "setcompleter")

cmds = []
resume = {}

class Console(ol.Object):

    def __init__(self):
        super().__init__()
        self.ready = threading.Event()
        ol.bus.bus.add(self)

    def announce(self, txt):
        pass

    def direct(self, txt):
        print(txt.rstrip())

    def input(self):
        k = ol.krn.get_kernel()
        while 1:
            try:
                event = self.poll()
            except EOFError:
                print("")
                continue
            event.orig = repr(self)
            k.queue.put(event)
            event.wait()

    def poll(self):
        e = ol.evt.Event()
        e.orig = repr(self)
        e.txt = input("> ")
        return e

    def say(self, channel, txt):
        self.direct(txt)

    def start(self):
        k = ol.krn.get_kernel()
        setcompleter(k.cmds)
        ol.tsk.launch(self.input)

def complete(text, state):
    matches = []
    if text:
        matches = [s for s in cmds if s and s.startswith(text)]
    else:
        matches = cmds[:]
    try:
        return matches[state]
    except IndexError:
        return None

def getcompleter():
    return readline.get_completer()

def setcompleter(commands):
    cmds.extend(commands)
    readline.set_completer(complete)
    readline.parse_and_bind("tab: complete")
    atexit.register(lambda: readline.set_completer(None))
