from __future__ import print_function
__version__ = "0.1.2"
import sys

def info():
    print("rweb: rsensor web application")

def log_message(lvl, msg, *args):
    global VERBOSE
    if VERBOSE >= lvl:
        print("<%d> %s" % (lvl, APP), time.strftime("%Y-%m-%d %H:%M:%S -"), msg, ", ".join(map(str,args)))
        sys.stdout.flush()
