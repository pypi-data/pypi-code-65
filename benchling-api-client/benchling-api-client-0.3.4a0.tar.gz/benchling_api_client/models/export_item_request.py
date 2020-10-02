from typing import Any, Dict

import attr


@attr.s(auto_attribs=True)
class ExportItemRequest:
    """  """

    id: str

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        return {
            "id": id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ExportItemRequest":
        id = d["id"]

        return ExportItemRequest(
            id=id,
        )
