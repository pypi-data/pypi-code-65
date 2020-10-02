from typing import Any, Dict, List, Optional

import attr

from ..models.dropdown_summary import DropdownSummary


@attr.s(auto_attribs=True)
class DropdownSummaryList:
    """  """

    dropdowns: Optional[List[DropdownSummary]] = None
    next_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.dropdowns is None:
            dropdowns = None
        else:
            dropdowns = []
            for dropdowns_item_data in self.dropdowns:
                dropdowns_item = dropdowns_item_data.to_dict()

                dropdowns.append(dropdowns_item)

        next_token = self.next_token

        return {
            "dropdowns": dropdowns,
            "nextToken": next_token,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DropdownSummaryList":
        dropdowns = []
        for dropdowns_item_data in d.get("dropdowns") or []:
            dropdowns_item = DropdownSummary.from_dict(dropdowns_item_data)

            dropdowns.append(dropdowns_item)

        next_token = d.get("nextToken")

        return DropdownSummaryList(
            dropdowns=dropdowns,
            next_token=next_token,
        )
