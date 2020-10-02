from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class SchemaField:
    """  """

    is_required: Optional[bool] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        is_required = self.is_required
        name = self.name

        return {
            "isRequired": is_required,
            "name": name,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SchemaField":
        is_required = d.get("isRequired")

        name = d.get("name")

        return SchemaField(
            is_required=is_required,
            name=name,
        )
