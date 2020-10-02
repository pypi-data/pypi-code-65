from typing import Any, Dict, List

import attr


@attr.s(auto_attribs=True)
class PlateUnarchiveRequest:
    """  """

    plate_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        plate_ids = self.plate_ids

        return {
            "plateIds": plate_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PlateUnarchiveRequest":
        plate_ids = d["plateIds"]

        return PlateUnarchiveRequest(
            plate_ids=plate_ids,
        )
