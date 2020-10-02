from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class UserSummary:
    """  """

    name: Optional[str] = None
    handle: Optional[str] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        handle = self.handle
        id = self.id

        return {
            "name": name,
            "handle": handle,
            "id": id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "UserSummary":
        name = d.get("name")

        handle = d.get("handle")

        id = d.get("id")

        return UserSummary(
            name=name,
            handle=handle,
            id=id,
        )
