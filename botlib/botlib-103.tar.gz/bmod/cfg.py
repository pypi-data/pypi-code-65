# BOTLIB - framework to program bots
#
#

import ol

k = ol.krn.get_kernel()

def cfg(event):
    if event.prs.sets:
        ol.update(k.cfg, event.prs.sets)
        ol.save(k.cfg)
    event.reply(ol.format(k.cfg, skip=["otxt", "sets"]))

def icfg(event):
    try:
        from bot.irc import Cfg
    except ImportError:
        from ol.krn import Cfg
    c = Cfg()
    ol.dbs.last(c)
    o = ol.Default()
    ol.prs.parse(o, event.prs.otxt)
    if o.sets:
        ol.update(c, o.sets)
        ol.save(c)
    event.reply(ol.format(c, skip=["username", "realname"]))
