from typing import Any, Dict, List, Optional

import attr

from ..models.plate import Plate


@attr.s(auto_attribs=True)
class PlateBulkGetResponse:
    """  """

    plates: Optional[List[Plate]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.plates is None:
            plates = None
        else:
            plates = []
            for plates_item_data in self.plates:
                plates_item = plates_item_data.to_dict()

                plates.append(plates_item)

        return {
            "plates": plates,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PlateBulkGetResponse":
        plates = []
        for plates_item_data in d.get("plates") or []:
            plates_item = Plate.from_dict(plates_item_data)

            plates.append(plates_item)

        return PlateBulkGetResponse(
            plates=plates,
        )
