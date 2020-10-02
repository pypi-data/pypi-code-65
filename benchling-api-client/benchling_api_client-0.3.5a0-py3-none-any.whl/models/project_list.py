from typing import Any, Dict, List, Optional

import attr

from ..models.project import Project


@attr.s(auto_attribs=True)
class ProjectList:
    """  """

    next_token: Optional[str] = None
    projects: Optional[List[Project]] = None

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
    def from_dict(d: Dict[str, Any]) -> "ProjectList":
        next_token = d.get("nextToken")

        projects = []
        for projects_item_data in d.get("projects") or []:
            projects_item = Project.from_dict(projects_item_data)

            projects.append(projects_item)

        return ProjectList(
            next_token=next_token,
            projects=projects,
        )
