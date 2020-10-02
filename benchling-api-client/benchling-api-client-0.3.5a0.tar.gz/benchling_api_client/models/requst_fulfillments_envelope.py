from typing import Any, Dict, List, Optional

import attr

from ..models.request_fulfillment import RequestFulfillment


@attr.s(auto_attribs=True)
class RequstFulfillmentsEnvelope:
    """ An object containing an array of RequestFulfillments """

    request_fulfillments: List[RequestFulfillment]
    next_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        request_fulfillments = []
        for request_fulfillments_item_data in self.request_fulfillments:
            request_fulfillments_item = request_fulfillments_item_data.to_dict()

            request_fulfillments.append(request_fulfillments_item)

        next_token = self.next_token

        return {
            "requestFulfillments": request_fulfillments,
            "nextToken": next_token,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RequstFulfillmentsEnvelope":
        request_fulfillments = []
        for request_fulfillments_item_data in d["requestFulfillments"]:
            request_fulfillments_item = RequestFulfillment.from_dict(request_fulfillments_item_data)

            request_fulfillments.append(request_fulfillments_item)

        next_token = d.get("nextToken")

        return RequstFulfillmentsEnvelope(
            request_fulfillments=request_fulfillments,
            next_token=next_token,
        )
