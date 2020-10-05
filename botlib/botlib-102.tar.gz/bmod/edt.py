# OLIB - object library
#
#

import ol

k = ol.krn.get_kernel()

def edt(event):
    if not event.args:
        f = ol.utl.list_files(ol.wd)
        if f:
            event.reply(f)
        return
    cn = event.args[0]
    if "." not in cn:
        cn = ol.get(k.types, cn)
    try:
        l = ol.dbs.lasttype(cn)
    except IndexError:
        return
    if not l:
        try:
            c = ol.get_cls(cn)
            l = c()
            event.reply("created %s" % cn)
        except ol.ENOCLASS:
            event.reply(ol.utl.list_files(ol.wd))
            return
    if not event.prs.sets:
        event.reply(l)
        return
    ol.edit(l, event.prs.sets)
    ol.save(l)
    event.reply("ok")
