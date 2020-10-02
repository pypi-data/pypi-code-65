from typing import Any, Dict, List, Optional

import attr

from ..models.request import Request


@attr.s(auto_attribs=True)
class RequestsBulkGetResponseBody:
    """  """

    requests: Optional[List[Request]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.requests is None:
            requests = None
        else:
            requests = []
            for requests_item_data in self.requests:
                requests_item = requests_item_data.to_dict()

                requests.append(requests_item)

        return {
            "requests": requests,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RequestsBulkGetResponseBody":
        requests = []
        for requests_item_data in d.get("requests") or []:
            requests_item = Request.from_dict(requests_item_data)

            requests.append(requests_item)

        return RequestsBulkGetResponseBody(
            requests=requests,
        )
