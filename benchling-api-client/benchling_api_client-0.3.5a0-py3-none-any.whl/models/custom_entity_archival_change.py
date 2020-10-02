from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class CustomEntityArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of custom entities along with any IDs of batches that were archived (or unarchived)."""

    custom_entity_ids: Optional[List[str]] = None
    batch_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.custom_entity_ids is None:
            custom_entity_ids = None
        else:
            custom_entity_ids = self.custom_entity_ids

        if self.batch_ids is None:
            batch_ids = None
        else:
            batch_ids = self.batch_ids

        return {
            "customEntityIds": custom_entity_ids,
            "batchIds": batch_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "CustomEntityArchivalChange":
        custom_entity_ids = d.get("customEntityIds")

        batch_ids = d.get("batchIds")

        return CustomEntityArchivalChange(
            custom_entity_ids=custom_entity_ids,
            batch_ids=batch_ids,
        )
