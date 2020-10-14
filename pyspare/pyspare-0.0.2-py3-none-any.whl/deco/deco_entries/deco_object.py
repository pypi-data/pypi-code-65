from typing import Callable, List, Tuple

from palett import Preset
from palett.presets import FRESH, PLANET
from texting import COLF, RTSP
from texting.enum.brackets import BRC

from pyspare.deco.deco_entries.deco_dict import deco_dict


def deco_object(
        ob: dict,
        key_read: Callable = None,
        read: Callable = None,
        presets: Tuple[Preset] = (FRESH, PLANET),
        effects: List[str] = None,
        delim: str = COLF,
        bracket: int = BRC,
        ansi: bool = False,
        dash: str = RTSP
):
    lex = ob.__dict__ \
        if hasattr(ob, '__dict__') \
        else {s: getattr(ob, s) for s in ob.__slots__} \
        if hasattr(ob, '__slots__') \
        else {}
    stringed = deco_dict(lex,
                         key_read=key_read,
                         read=read,
                         presets=presets,
                         effects=effects,
                         delim=delim,
                         bracket=bracket,
                         ansi=ansi,
                         dash=dash) if lex else str(ob)
    return f'[{type(ob).__name__}] {stringed}'
