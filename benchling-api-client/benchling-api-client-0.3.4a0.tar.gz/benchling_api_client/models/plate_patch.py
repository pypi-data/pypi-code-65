from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class PlatePatch:
    """  """

    fields: Optional[Dict[Any, Any]] = None
    name: Optional[str] = None
    parent_storage_id: Optional[str] = None
    project_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        fields = self.fields if self.fields else None

        name = self.name
        parent_storage_id = self.parent_storage_id
        project_id = self.project_id

        return {
            "fields": fields,
            "name": name,
            "parentStorageId": parent_storage_id,
            "projectId": project_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PlatePatch":
        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        name = d.get("name")

        parent_storage_id = d.get("parentStorageId")

        project_id = d.get("projectId")

        return PlatePatch(
            fields=fields,
            name=name,
            parent_storage_id=parent_storage_id,
            project_id=project_id,
        )
