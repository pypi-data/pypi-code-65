import datetime
from typing import Any, Dict, Optional, cast

import attr
from dateutil.parser import isoparse

from ..models.archive_record import ArchiveRecord
from ..models.schema_summary import SchemaSummary
from ..models.user_summary import UserSummary


@attr.s(auto_attribs=True)
class Box:
    """  """

    archive_record: Optional[ArchiveRecord] = None
    barcode: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    creator: Optional[UserSummary] = None
    fields: Optional[Dict[Any, Any]] = None
    id: Optional[str] = None
    modified_at: Optional[datetime.datetime] = None
    size: Optional[int] = None
    filled_positions: Optional[int] = None
    empty_positions: Optional[int] = None
    empty_containers: Optional[int] = None
    name: Optional[str] = None
    parent_storage_id: Optional[str] = None
    project_id: Optional[str] = None
    schema: Optional[SchemaSummary] = None
    web_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        archive_record = self.archive_record.to_dict() if self.archive_record else None

        barcode = self.barcode
        created_at = self.created_at.isoformat() if self.created_at else None

        creator = self.creator.to_dict() if self.creator else None

        fields = self.fields if self.fields else None

        id = self.id
        modified_at = self.modified_at.isoformat() if self.modified_at else None

        size = self.size
        filled_positions = self.filled_positions
        empty_positions = self.empty_positions
        empty_containers = self.empty_containers
        name = self.name
        parent_storage_id = self.parent_storage_id
        project_id = self.project_id
        schema = self.schema.to_dict() if self.schema else None

        web_url = self.web_url

        return {
            "archiveRecord": archive_record,
            "barcode": barcode,
            "createdAt": created_at,
            "creator": creator,
            "fields": fields,
            "id": id,
            "modifiedAt": modified_at,
            "size": size,
            "filledPositions": filled_positions,
            "emptyPositions": empty_positions,
            "emptyContainers": empty_containers,
            "name": name,
            "parentStorageId": parent_storage_id,
            "projectId": project_id,
            "schema": schema,
            "webURL": web_url,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Box":
        archive_record = None
        if d.get("archiveRecord") is not None:
            archive_record = ArchiveRecord.from_dict(cast(Dict[str, Any], d.get("archiveRecord")))

        barcode = d.get("barcode")

        created_at = None
        if d.get("createdAt") is not None:
            created_at = isoparse(cast(str, d.get("createdAt")))

        creator = None
        if d.get("creator") is not None:
            creator = UserSummary.from_dict(cast(Dict[str, Any], d.get("creator")))

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        id = d.get("id")

        modified_at = None
        if d.get("modifiedAt") is not None:
            modified_at = isoparse(cast(str, d.get("modifiedAt")))

        size = d.get("size")

        filled_positions = d.get("filledPositions")

        empty_positions = d.get("emptyPositions")

        empty_containers = d.get("emptyContainers")

        name = d.get("name")

        parent_storage_id = d.get("parentStorageId")

        project_id = d.get("projectId")

        schema = None
        if d.get("schema") is not None:
            schema = SchemaSummary.from_dict(cast(Dict[str, Any], d.get("schema")))

        web_url = d.get("webURL")

        return Box(
            archive_record=archive_record,
            barcode=barcode,
            created_at=created_at,
            creator=creator,
            fields=fields,
            id=id,
            modified_at=modified_at,
            size=size,
            filled_positions=filled_positions,
            empty_positions=empty_positions,
            empty_containers=empty_containers,
            name=name,
            parent_storage_id=parent_storage_id,
            project_id=project_id,
            schema=schema,
            web_url=web_url,
        )
