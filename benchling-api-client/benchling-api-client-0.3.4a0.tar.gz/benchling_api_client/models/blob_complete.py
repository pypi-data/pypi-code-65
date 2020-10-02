from typing import Any, Dict, List, Optional

import attr

from ..models.blob_part import BlobPart


@attr.s(auto_attribs=True)
class BlobComplete:
    """  """

    parts: Optional[List[BlobPart]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.parts is None:
            parts = None
        else:
            parts = []
            for parts_item_data in self.parts:
                parts_item = parts_item_data.to_dict()

                parts.append(parts_item)

        return {
            "parts": parts,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BlobComplete":
        parts = []
        for parts_item_data in d.get("parts") or []:
            parts_item = BlobPart.from_dict(parts_item_data)

            parts.append(parts_item)

        return BlobComplete(
            parts=parts,
        )
