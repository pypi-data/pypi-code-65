from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class BlobUrl:
    """  """

    download_url: Optional[str] = None
    expires_at: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        download_url = self.download_url
        expires_at = self.expires_at

        return {
            "downloadURL": download_url,
            "expiresAt": expires_at,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BlobUrl":
        download_url = d.get("downloadURL")

        expires_at = d.get("expiresAt")

        return BlobUrl(
            download_url=download_url,
            expires_at=expires_at,
        )
