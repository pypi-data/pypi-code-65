from typing import Any, Dict

import attr


@attr.s(auto_attribs=True)
class ArchiveRecord:
    """  """

    reason: str

    def to_dict(self) -> Dict[str, Any]:
        reason = self.reason

        return {
            "reason": reason,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ArchiveRecord":
        reason = d["reason"]

        return ArchiveRecord(
            reason=reason,
        )
