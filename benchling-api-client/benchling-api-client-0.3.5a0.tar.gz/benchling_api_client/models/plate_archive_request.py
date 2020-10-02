from typing import Any, Dict, List, Optional

import attr

from ..models.reason1 import Reason1


@attr.s(auto_attribs=True)
class PlateArchiveRequest:
    """  """

    plate_ids: List[str]
    reason: Reason1
    should_remove_barcodes: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        plate_ids = self.plate_ids

        reason = self.reason.value

        should_remove_barcodes = self.should_remove_barcodes

        return {
            "plateIds": plate_ids,
            "reason": reason,
            "shouldRemoveBarcodes": should_remove_barcodes,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PlateArchiveRequest":
        plate_ids = d["plateIds"]

        reason = Reason1(d["reason"])

        should_remove_barcodes = d.get("shouldRemoveBarcodes")

        return PlateArchiveRequest(
            plate_ids=plate_ids,
            reason=reason,
            should_remove_barcodes=should_remove_barcodes,
        )
