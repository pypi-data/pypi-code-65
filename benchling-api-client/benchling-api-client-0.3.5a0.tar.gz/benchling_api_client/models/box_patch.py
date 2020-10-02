from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class BoxPatch:
    """  """

    name: Optional[str] = None
    fields: Optional[Dict[Any, Any]] = None
    parent_storage_id: Optional[str] = None
    project_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        fields = self.fields if self.fields else None

        parent_storage_id = self.parent_storage_id
        project_id = self.project_id

        return {
            "name": name,
            "fields": fields,
            "parentStorageId": parent_storage_id,
            "projectId": project_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BoxPatch":
        name = d.get("name")

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        parent_storage_id = d.get("parentStorageId")

        project_id = d.get("projectId")

        return BoxPatch(
            name=name,
            fields=fields,
            parent_storage_id=parent_storage_id,
            project_id=project_id,
        )
