from typing import Any, Dict, Optional, cast

import attr

from ..models.schema_summary import SchemaSummary


@attr.s(auto_attribs=True)
class BoxCreate:
    """  """

    barcode: Optional[str] = None
    fields: Optional[Dict[Any, Any]] = None
    name: Optional[str] = None
    parent_storage_id: Optional[str] = None
    project_id: Optional[str] = None
    schema: Optional[SchemaSummary] = None

    def to_dict(self) -> Dict[str, Any]:
        barcode = self.barcode
        fields = self.fields if self.fields else None

        name = self.name
        parent_storage_id = self.parent_storage_id
        project_id = self.project_id
        schema = self.schema.to_dict() if self.schema else None

        return {
            "barcode": barcode,
            "fields": fields,
            "name": name,
            "parentStorageId": parent_storage_id,
            "projectId": project_id,
            "schema": schema,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BoxCreate":
        barcode = d.get("barcode")

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        name = d.get("name")

        parent_storage_id = d.get("parentStorageId")

        project_id = d.get("projectId")

        schema = None
        if d.get("schema") is not None:
            schema = SchemaSummary.from_dict(cast(Dict[str, Any], d.get("schema")))

        return BoxCreate(
            barcode=barcode,
            fields=fields,
            name=name,
            parent_storage_id=parent_storage_id,
            project_id=project_id,
            schema=schema,
        )
