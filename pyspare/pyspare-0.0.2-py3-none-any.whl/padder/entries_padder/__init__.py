from aryth.bound_entries import max_by
from texting import SP, lange
from veho.entries import mapper

from pyspare.padder.string_padder import to_lpad, to_pad


def entries_padder(text, ansi=False, fill=SP):
    lpad, pad = to_lpad(ansi=ansi, fill=fill), to_pad(ansi=ansi, fill=fill)
    kw, vw = max_by(text, lange if ansi else len)
    return mapper(text, lambda x: lpad(x, kw), lambda tx: pad(tx, vw, tx))
