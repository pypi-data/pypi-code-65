from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class BlobPart:
    """  """

    part_number: Optional[int] = None
    e_tag: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        part_number = self.part_number
        e_tag = self.e_tag

        return {
            "partNumber": part_number,
            "eTag": e_tag,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BlobPart":
        part_number = d.get("partNumber")

        e_tag = d.get("eTag")

        return BlobPart(
            part_number=part_number,
            e_tag=e_tag,
        )
