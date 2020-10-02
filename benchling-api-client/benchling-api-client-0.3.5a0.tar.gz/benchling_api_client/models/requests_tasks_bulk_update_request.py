from typing import Any, Dict, List, Optional

import attr

from ..models.requests_task_base import RequestsTaskBase


@attr.s(auto_attribs=True)
class RequestsTasksBulkUpdateRequest:
    """A request body for bulk updating request tasks."""

    tasks: Optional[List[RequestsTaskBase]] = None

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
    def from_dict(d: Dict[str, Any]) -> "RequestsTasksBulkUpdateRequest":
        tasks = []
        for tasks_item_data in d.get("tasks") or []:
            tasks_item = RequestsTaskBase.from_dict(tasks_item_data)

            tasks.append(tasks_item)

        return RequestsTasksBulkUpdateRequest(
            tasks=tasks,
        )
