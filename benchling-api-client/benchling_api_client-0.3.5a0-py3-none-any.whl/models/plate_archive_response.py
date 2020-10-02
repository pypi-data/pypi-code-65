from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class PlateArchiveResponse:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of plates along with any IDs of containers that were archived / unarchived."""

    plate_ids: Optional[List[str]] = None
    container_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.plate_ids is None:
            plate_ids = None
        else:
            plate_ids = self.plate_ids

        if self.container_ids is None:
            container_ids = None
        else:
            container_ids = self.container_ids

        return {
            "plateIds": plate_ids,
            "containerIds": container_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PlateArchiveResponse":
        plate_ids = d.get("plateIds")

        container_ids = d.get("containerIds")

        return PlateArchiveResponse(
            plate_ids=plate_ids,
            container_ids=container_ids,
        )
