from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class DropdownSummary:
    """  """

    name: Optional[str] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        id = self.id

        return {
            "name": name,
            "id": id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DropdownSummary":
        name = d.get("name")

        id = d.get("id")

        return DropdownSummary(
            name=name,
            id=id,
        )
