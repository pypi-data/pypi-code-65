from typing import Any, Dict, List, Optional

import attr

from ..models.folder import Folder


@attr.s(auto_attribs=True)
class FolderList:
    """  """

    next_token: Optional[str] = None
    projects: Optional[List[Folder]] = None

    def to_dict(self) -> Dict[str, Any]:
        next_token = self.next_token
        if self.projects is None:
            projects = None
        else:
            projects = []
            for projects_item_data in self.projects:
                projects_item = projects_item_data.to_dict()

                projects.append(projects_item)

        return {
            "nextToken": next_token,
            "projects": projects,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "FolderList":
        next_token = d.get("nextToken")

        projects = []
        for projects_item_data in d.get("projects") or []:
            projects_item = Folder.from_dict(projects_item_data)

            projects.append(projects_item)

        return FolderList(
            next_token=next_token,
            projects=projects,
        )
