from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class RequestsTaskBase:
    """A request task."""

    id: Optional[str] = None
    fields: Optional[Dict[Any, Any]] = None
    sample_group_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        fields = self.fields if self.fields else None

        if self.sample_group_ids is None:
            sample_group_ids = None
        else:
            sample_group_ids = self.sample_group_ids

        return {
            "id": id,
            "fields": fields,
            "sampleGroupIds": sample_group_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RequestsTaskBase":
        id = d.get("id")

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        sample_group_ids = d.get("sampleGroupIds")

        return RequestsTaskBase(
            id=id,
            fields=fields,
            sample_group_ids=sample_group_ids,
        )
