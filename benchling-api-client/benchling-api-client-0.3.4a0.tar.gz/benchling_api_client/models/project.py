from typing import Any, Dict, Optional, Union, cast

import attr

from ..models.archive_record import ArchiveRecord
from ..models.organization import Organization
from ..models.user_summary import UserSummary


@attr.s(auto_attribs=True)
class Project:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    archive_record: Optional[ArchiveRecord] = None
    owner: Optional[Union[Optional[Organization], Optional[UserSummary]]] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        archive_record = self.archive_record.to_dict() if self.archive_record else None

        if self.owner is None:
            owner: Optional[Union[Optional[Organization], Optional[UserSummary]]] = None
        elif isinstance(self.owner, Organization):
            owner = self.owner.to_dict() if self.owner else None

        else:
            owner = self.owner.to_dict() if self.owner else None

        return {
            "id": id,
            "name": name,
            "archiveRecord": archive_record,
            "owner": owner,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Project":
        id = d.get("id")

        name = d.get("name")

        archive_record = None
        if d.get("archiveRecord") is not None:
            archive_record = ArchiveRecord.from_dict(cast(Dict[str, Any], d.get("archiveRecord")))

        def _parse_owner(data: Dict[str, Any]) -> Optional[Union[Optional[Organization], Optional[UserSummary]]]:
            owner: Optional[Union[Optional[Organization], Optional[UserSummary]]]
            try:
                owner = None
                if d.get("owner") is not None:
                    owner = Organization.from_dict(cast(Dict[str, Any], d.get("owner")))

                return owner
            except:  # noqa: E722
                pass
            owner = None
            if d.get("owner") is not None:
                owner = UserSummary.from_dict(cast(Dict[str, Any], d.get("owner")))

            return owner

        owner = _parse_owner(d.get("owner"))

        return Project(
            id=id,
            name=name,
            archive_record=archive_record,
            owner=owner,
        )
