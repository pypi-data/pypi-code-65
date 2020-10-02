import datetime
from typing import Any, Dict, List, Union

import attr
from dateutil.parser import isoparse


@attr.s(auto_attribs=True)
class Request:
    """  """

    id: str
    created_at: datetime.datetime
    display_id: str
    assignees: List[Union[Dict[Any, Any], Dict[Any, Any]]]
    web_url: str

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        created_at = self.created_at.isoformat()

        display_id = self.display_id
        assignees = []
        for assignees_item_data in self.assignees:
            if isinstance(assignees_item_data, Dict[Any, Any]):
                assignees_item = assignees_item_data

            else:
                assignees_item = assignees_item_data

            assignees.append(assignees_item)

        web_url = self.web_url

        return {
            "id": id,
            "createdAt": created_at,
            "displayId": display_id,
            "assignees": assignees,
            "webURL": web_url,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Request":
        id = d["id"]

        created_at = isoparse(d["createdAt"])

        display_id = d["displayId"]

        assignees = []
        for assignees_item_data in d["assignees"]:

            def _parse_assignees_item(data: Dict[str, Any]) -> Union[Dict[Any, Any], Dict[Any, Any]]:
                assignees_item: Union[Dict[Any, Any], Dict[Any, Any]]
                try:
                    assignees_item = assignees_item_data

                    return assignees_item
                except:  # noqa: E722
                    pass
                assignees_item = assignees_item_data

                return assignees_item

            assignees_item = _parse_assignees_item(assignees_item_data)

            assignees.append(assignees_item)

        web_url = d["webURL"]

        return Request(
            id=id,
            created_at=created_at,
            display_id=display_id,
            assignees=assignees,
            web_url=web_url,
        )
