# GENOCIDE - the king of the netherlands commits genocide - OTP-CR-117/19/001 - otp.informationdesk@icc-cpi.int - https://genocide.rtfd.io
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
    nr = -1
    try:
        args = event.args[1:]
    except:
        args = []
    for otype in event.types:
        for o in ol.dbs.find(otype, event.prs.gets, event.prs.index, event.prs.timed):
            nr += 1
            if "f" in event.prs.opts:
                pure = False
            else:
                pure = True
            txt = "%s %s" % (str(nr), ol.format(o, args or ol.keys(o), False, event.prs.skip))
            if "t" in event.prs.opts:
                txt = txt + " %s" % (ol.tms.elapsed(time.time() - ol.tms.fntime(o.stp)))
            event.reply(txt)
