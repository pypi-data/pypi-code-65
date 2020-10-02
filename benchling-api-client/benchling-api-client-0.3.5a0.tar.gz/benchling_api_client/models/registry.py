from typing import Any, Dict, Optional, cast

import attr

from ..models.organization import Organization


@attr.s(auto_attribs=True)
class Registry:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    owner: Optional[Organization] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        owner = self.owner.to_dict() if self.owner else None

        return {
            "id": id,
            "name": name,
            "owner": owner,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Registry":
        id = d.get("id")

        name = d.get("name")

        owner = None
        if d.get("owner") is not None:
            owner = Organization.from_dict(cast(Dict[str, Any], d.get("owner")))

        return Registry(
            id=id,
            name=name,
            owner=owner,
        )
