from typing import Any, Dict, List, Optional

import attr

from ..models.requests_task import RequestsTask


@attr.s(auto_attribs=True)
class RequestsTasksBulkUpdateResponse:
    """  """

    tasks: Optional[List[RequestsTask]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.tasks is None:
            tasks = None
        else:
            tasks = []
            for tasks_item_data in self.tasks:
                tasks_item = tasks_item_data.to_dict()

                tasks.append(tasks_item)

        return {
            "tasks": tasks,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RequestsTasksBulkUpdateResponse":
        tasks = []
        for tasks_item_data in d.get("tasks") or []:
            tasks_item = RequestsTask.from_dict(tasks_item_data)

            tasks.append(tasks_item)

        return RequestsTasksBulkUpdateResponse(
            tasks=tasks,
        )
