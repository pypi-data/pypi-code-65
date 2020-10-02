from typing import Any, Dict

import attr


@attr.s(auto_attribs=True)
class Mixture:
    """  """

    def to_dict(self) -> Dict[str, Any]:

        return {}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Mixture":
        return Mixture()
