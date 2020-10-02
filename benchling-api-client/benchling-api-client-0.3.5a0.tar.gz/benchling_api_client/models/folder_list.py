from typing import Any, Dict, List, Optional

import attr

from ..models.folder import Folder


@attr.s(auto_attribs=True)
class FolderList:
    """  """

    next_token: Optional[str] = None
    folders: Optional[List[Folder]] = None

    def to_dict(self) -> Dict[str, Any]:
        next_token = self.next_token
        if self.folders is None:
            folders = None
        else:
            folders = []
            for folders_item_data in self.folders:
                folders_item = folders_item_data.to_dict()

                folders.append(folders_item)

        return {
            "nextToken": next_token,
            "folders": folders,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "FolderList":
        next_token = d.get("nextToken")

        folders = []
        for folders_item_data in d.get("folders") or []:
            folders_item = Folder.from_dict(folders_item_data)

            folders.append(folders_item)

        return FolderList(
            next_token=next_token,
            folders=folders,
        )
