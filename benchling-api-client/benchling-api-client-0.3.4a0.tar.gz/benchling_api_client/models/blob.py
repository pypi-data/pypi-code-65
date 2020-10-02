from typing import Any, Dict, Optional

import attr

from ..models.type123 import Type123
from ..models.upload_status import UploadStatus


@attr.s(auto_attribs=True)
class Blob:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[Type123] = None
    mime_type: Optional[str] = None
    upload_status: Optional[UploadStatus] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        type = self.type.value if self.type else None

        mime_type = self.mime_type
        upload_status = self.upload_status.value if self.upload_status else None

        return {
            "id": id,
            "name": name,
            "type": type,
            "mimeType": mime_type,
            "uploadStatus": upload_status,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Blob":
        id = d.get("id")

        name = d.get("name")

        type = None
        if d.get("type") is not None:
            type = Type123(d.get("type"))

        mime_type = d.get("mimeType")

        upload_status = None
        if d.get("uploadStatus") is not None:
            upload_status = UploadStatus(d.get("uploadStatus"))

        return Blob(
            id=id,
            name=name,
            type=type,
            mime_type=mime_type,
            upload_status=upload_status,
        )
