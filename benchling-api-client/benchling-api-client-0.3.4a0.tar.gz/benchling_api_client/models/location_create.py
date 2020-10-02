from typing import Any, Dict, Optional, cast

import attr

from ..models.fields import Fields


@attr.s(auto_attribs=True)
class LocationCreate:
    """  """

    name: str
    schema_id: str
    barcode: Optional[str] = None
    fields: Optional[Fields] = None
    parent_storage_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        schema_id = self.schema_id
        barcode = self.barcode
        fields = self.fields.to_dict() if self.fields else None

        parent_storage_id = self.parent_storage_id

        return {
            "name": name,
            "schemaId": schema_id,
            "barcode": barcode,
            "fields": fields,
            "parentStorageId": parent_storage_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "LocationCreate":
        name = d["name"]

        schema_id = d["schemaId"]

        barcode = d.get("barcode")

        fields = None
        if d.get("fields") is not None:
            fields = Fields.from_dict(cast(Dict[str, Any], d.get("fields")))

        parent_storage_id = d.get("parentStorageId")

        return LocationCreate(
            name=name,
            schema_id=schema_id,
            barcode=barcode,
            fields=fields,
            parent_storage_id=parent_storage_id,
        )
