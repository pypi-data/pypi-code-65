from typing import Any, Dict, Optional, cast

import attr

from ..models.fields import Fields


@attr.s(auto_attribs=True)
class LocationUpdate:
    """  """

    fields: Optional[Fields] = None
    name: Optional[str] = None
    parent_storage_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        fields = self.fields.to_dict() if self.fields else None

        name = self.name
        parent_storage_id = self.parent_storage_id

        return {
            "fields": fields,
            "name": name,
            "parentStorageId": parent_storage_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "LocationUpdate":
        fields = None
        if d.get("fields") is not None:
            fields = Fields.from_dict(cast(Dict[str, Any], d.get("fields")))

        name = d.get("name")

        parent_storage_id = d.get("parentStorageId")

        return LocationUpdate(
            fields=fields,
            name=name,
            parent_storage_id=parent_storage_id,
        )
