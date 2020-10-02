from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class Folder:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    parent_folder_id: Optional[str] = None
    project_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        parent_folder_id = self.parent_folder_id
        project_id = self.project_id

        return {
            "id": id,
            "name": name,
            "parentFolderId": parent_folder_id,
            "projectId": project_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Folder":
        id = d.get("id")

        name = d.get("name")

        parent_folder_id = d.get("parentFolderId")

        project_id = d.get("projectId")

        return Folder(
            id=id,
            name=name,
            parent_folder_id=parent_folder_id,
            project_id=project_id,
        )
