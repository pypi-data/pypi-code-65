from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class LocationArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of locations along with any IDs of locations, boxes, plates, containers that were archived."""

    location_ids: Optional[List[str]] = None
    box_ids: Optional[List[str]] = None
    plate_ids: Optional[List[str]] = None
    container_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.location_ids is None:
            location_ids = None
        else:
            location_ids = self.location_ids

        if self.box_ids is None:
            box_ids = None
        else:
            box_ids = self.box_ids

        if self.plate_ids is None:
            plate_ids = None
        else:
            plate_ids = self.plate_ids

        if self.container_ids is None:
            container_ids = None
        else:
            container_ids = self.container_ids

        return {
            "locationIds": location_ids,
            "boxIds": box_ids,
            "plateIds": plate_ids,
            "containerIds": container_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "LocationArchivalChange":
        location_ids = d.get("locationIds")

        box_ids = d.get("boxIds")

        plate_ids = d.get("plateIds")

        container_ids = d.get("containerIds")

        return LocationArchivalChange(
            location_ids=location_ids,
            box_ids=box_ids,
            plate_ids=plate_ids,
            container_ids=container_ids,
        )
