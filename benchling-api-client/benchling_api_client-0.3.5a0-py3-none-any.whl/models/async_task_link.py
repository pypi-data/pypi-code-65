from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class AsyncTaskLink:
    """  """

    task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        task_id = self.task_id

        return {
            "taskId": task_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AsyncTaskLink":
        task_id = d.get("taskId")

        return AsyncTaskLink(
            task_id=task_id,
        )
