from dataclasses import asdict, dataclass
from numbers import Number
from typing import Dict


@dataclass
class Approxable:
    @property
    def approxable_dict(self) -> Dict[str, Number]:
        ret = dict()
        dct = asdict(self)
        for k, v in dct.items():
            if isinstance(v, Number):
                ret[k] = v
            else:
                ret[k] = hash(v)
        return ret
