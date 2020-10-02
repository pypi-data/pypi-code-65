from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class CustomEntityRequestAuthorIds:
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
    def from_dict(d: Dict[str, Any]) -> "CustomEntityRequestAuthorIds":
        author_ids = d.get("authorIds")

        return CustomEntityRequestAuthorIds(
            author_ids=author_ids,
        )
