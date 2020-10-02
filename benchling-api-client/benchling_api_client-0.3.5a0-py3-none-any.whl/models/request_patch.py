import datetime
from typing import Any, Dict, List, Optional, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.request_status import RequestStatus


@attr.s(auto_attribs=True)
class RequestPatch:
    """  """

    request_status: Optional[RequestStatus] = None
    assignees: Optional[List[Union[Dict[Any, Any], Dict[Any, Any]]]] = None
    requestor_id: Optional[str] = None
    scheduled_on: Optional[datetime.date] = None
    project_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        request_status = self.request_status.value if self.request_status else None

        if self.assignees is None:
            assignees = None
        else:
            assignees = []
            for assignees_item_data in self.assignees:
                if isinstance(assignees_item_data, Dict[Any, Any]):
                    assignees_item = assignees_item_data

                else:
                    assignees_item = assignees_item_data

                assignees.append(assignees_item)

        requestor_id = self.requestor_id
        scheduled_on = self.scheduled_on.isoformat() if self.scheduled_on else None

        project_id = self.project_id

        return {
            "requestStatus": request_status,
            "assignees": assignees,
            "requestorId": requestor_id,
            "scheduledOn": scheduled_on,
            "projectId": project_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RequestPatch":
        request_status = None
        if d.get("requestStatus") is not None:
            request_status = RequestStatus(d.get("requestStatus"))

        assignees = []
        for assignees_item_data in d.get("assignees") or []:

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

        requestor_id = d.get("requestorId")

        scheduled_on = None
        if d.get("scheduledOn") is not None:
            scheduled_on = isoparse(cast(str, d.get("scheduledOn"))).date()

        project_id = d.get("projectId")

        return RequestPatch(
            request_status=request_status,
            assignees=assignees,
            requestor_id=requestor_id,
            scheduled_on=scheduled_on,
            project_id=project_id,
        )
