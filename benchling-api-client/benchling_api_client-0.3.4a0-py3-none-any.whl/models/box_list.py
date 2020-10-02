from typing import Any, Dict, List, Optional

import attr

from ..models.box import Box


@attr.s(auto_attribs=True)
class BoxList:
    """  """

    next_token: Optional[str] = None
    boxes: Optional[List[Box]] = None

    def to_dict(self) -> Dict[str, Any]:
        next_token = self.next_token
        if self.boxes is None:
            boxes = None
        else:
            boxes = []
            for boxes_item_data in self.boxes:
                boxes_item = boxes_item_data.to_dict()

                boxes.append(boxes_item)

        return {
            "nextToken": next_token,
            "boxes": boxes,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BoxList":
        next_token = d.get("nextToken")

        boxes = []
        for boxes_item_data in d.get("boxes") or []:
            boxes_item = Box.from_dict(boxes_item_data)

            boxes.append(boxes_item)

        return BoxList(
            next_token=next_token,
            boxes=boxes,
        )
