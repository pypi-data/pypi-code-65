from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class AssayRunPatch:
    """  """

    fields: Optional[Dict[Any, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        fields = self.fields if self.fields else None

        return {
            "fields": fields,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AssayRunPatch":
        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        return AssayRunPatch(
            fields=fields,
        )
