from typing import Any, Dict, Optional

import attr

from ..models.type123 import Type123


@attr.s(auto_attribs=True)
class BlobCreate:
    """  """

    name: str
    type: Type123
    data64: str
    md5: str
    mime_type: Optional[str] = "application/octet-stream"

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        type = self.type.value

        data64 = self.data64
        md5 = self.md5
        mime_type = self.mime_type

        return {
            "name": name,
            "type": type,
            "data64": data64,
            "md5": md5,
            "mimeType": mime_type,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BlobCreate":
        name = d["name"]

        type = Type123(d["type"])

        data64 = d["data64"]

        md5 = d["md5"]

        mime_type = d.get("mimeType")

        return BlobCreate(
            name=name,
            type=type,
            data64=data64,
            md5=md5,
            mime_type=mime_type,
        )
