# OLIB - object library
#
#

import ol
import os
import time

def fnd(event):
    if not event.args:
        wd = os.path.join(ol.wd, "store", "")
        ol.cdir(wd)
        fns = os.listdir(wd)
        fns = sorted({x.split(os.sep)[0].split(".")[-1].lower() for x in fns})
        if fns:
            event.reply(",".join(fns))
        return
    k = ol.krn.get_kernel()
    otype = event.args[0]
    otypes = ol.get(k.names, otype, [otype,])
    args = list(ol.keys(event.prs.gets))
    try:
        arg = event.args[1:]
    except ValueError:
        arg = []
    args.extend(arg)
    nr = -1
    for otype in otypes:
        for o in ol.dbs.find(otype, event.prs.gets, event.prs.index, event.prs.timed):
            nr += 1
            if "f" in event.prs.opts:
                pure = False
            else:
                pure = True
            txt = "%s %s" % (str(nr), ol.format(o, args, pure, event.prs.skip))
            if "t" in event.prs.opts:
                txt += " %s" % (ol.tms.elapsed(time.time() - ol.tms.fntime(o.__stp__)))
            event.reply(txt)
