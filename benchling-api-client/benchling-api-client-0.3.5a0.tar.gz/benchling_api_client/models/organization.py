from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class Organization:
    """  """

    handle: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        handle = self.handle
        id = self.id
        name = self.name

        return {
            "handle": handle,
            "id": id,
            "name": name,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Organization":
        handle = d.get("handle")

        id = d.get("id")

        name = d.get("name")

        return Organization(
            handle=handle,
            id=id,
            name=name,
        )
