from typing import Any, Dict, List, Optional, cast

import attr

from ..models.schema_summary import SchemaSummary


@attr.s(auto_attribs=True)
class RequestsTask:
    """A request task."""

    schema: Optional[SchemaSummary] = None
    id: Optional[str] = None
    fields: Optional[Dict[Any, Any]] = None
    sample_group_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        schema = self.schema.to_dict() if self.schema else None

        id = self.id
        fields = self.fields if self.fields else None

        if self.sample_group_ids is None:
            sample_group_ids = None
        else:
            sample_group_ids = self.sample_group_ids

        return {
            "schema": schema,
            "id": id,
            "fields": fields,
            "sampleGroupIds": sample_group_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RequestsTask":
        schema = None
        if d.get("schema") is not None:
            schema = SchemaSummary.from_dict(cast(Dict[str, Any], d.get("schema")))

        id = d.get("id")

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        sample_group_ids = d.get("sampleGroupIds")

        return RequestsTask(
            schema=schema,
            id=id,
            fields=fields,
            sample_group_ids=sample_group_ids,
        )
