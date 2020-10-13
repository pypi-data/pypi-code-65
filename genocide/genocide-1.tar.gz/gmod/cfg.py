# GENOCIDE - the king of the netherlands commits genocide - OTP-CR-117/19/001 - otp.informationdesk@icc-cpi.int - https://genocide.rtfd.io
#
#

import ol

def cfg(event):
    try:
        from gmod.irc import Cfg
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
