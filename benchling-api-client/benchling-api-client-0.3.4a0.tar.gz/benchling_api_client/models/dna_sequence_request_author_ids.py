from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class DnaSequenceRequestAuthorIds:
    """  """

    author_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.author_ids is None:
            author_ids = None
        else:
            author_ids = self.author_ids

        return {
            "authorIds": author_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DnaSequenceRequestAuthorIds":
        author_ids = d.get("authorIds")

        return DnaSequenceRequestAuthorIds(
            author_ids=author_ids,
        )
