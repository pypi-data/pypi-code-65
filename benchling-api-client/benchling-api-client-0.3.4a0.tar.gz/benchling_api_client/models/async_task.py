from typing import Any, Dict, Optional

import attr

from ..models.status1 import Status1


@attr.s(auto_attribs=True)
class AsyncTask:
    """  """

    status: Status1
    response: Optional[Dict[Any, Any]] = None
    message: Optional[str] = None
    errors: Optional[Dict[Any, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        response = self.response if self.response else None

        message = self.message
        errors = self.errors if self.errors else None

        return {
            "status": status,
            "response": response,
            "message": message,
            "errors": errors,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AsyncTask":
        status = Status1(d["status"])

        response = None
        if d.get("response") is not None:
            response = d.get("response")

        message = d.get("message")

        errors = None
        if d.get("errors") is not None:
            errors = d.get("errors")

        return AsyncTask(
            status=status,
            response=response,
            message=message,
            errors=errors,
        )
