import datetime
from typing import Any, Dict, List, Optional, cast

import attr
from dateutil.parser import isoparse

from ..models.container_content import ContainerContent
from ..models.schema_summary import SchemaSummary
from ..models.user_summary import UserSummary


@attr.s(auto_attribs=True)
class Well:
    """  """

    barcode: Optional[str] = None
    contents: Optional[List[ContainerContent]] = None
    created_at: Optional[datetime.datetime] = None
    creator: Optional[UserSummary] = None
    fields: Optional[Dict[Any, Any]] = None
    id: Optional[str] = None
    modified_at: Optional[datetime.datetime] = None
    name: Optional[str] = None
    parent_storage_id: Optional[str] = None
    parent_storage_schema: Optional[SchemaSummary] = None
    project_id: Optional[str] = None
    schema: Optional[SchemaSummary] = None
    volume: Optional[Dict[Any, Any]] = None
    web_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        barcode = self.barcode
        if self.contents is None:
            contents = None
        else:
            contents = []
            for contents_item_data in self.contents:
                contents_item = contents_item_data.to_dict()

                contents.append(contents_item)

        created_at = self.created_at.isoformat() if self.created_at else None

        creator = self.creator.to_dict() if self.creator else None

        fields = self.fields if self.fields else None

        id = self.id
        modified_at = self.modified_at.isoformat() if self.modified_at else None

        name = self.name
        parent_storage_id = self.parent_storage_id
        parent_storage_schema = self.parent_storage_schema.to_dict() if self.parent_storage_schema else None

        project_id = self.project_id
        schema = self.schema.to_dict() if self.schema else None

        volume = self.volume if self.volume else None

        web_url = self.web_url

        return {
            "barcode": barcode,
            "contents": contents,
            "createdAt": created_at,
            "creator": creator,
            "fields": fields,
            "id": id,
            "modifiedAt": modified_at,
            "name": name,
            "parentStorageId": parent_storage_id,
            "parentStorageSchema": parent_storage_schema,
            "projectId": project_id,
            "schema": schema,
            "volume": volume,
            "webURL": web_url,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Well":
        barcode = d.get("barcode")

        contents = []
        for contents_item_data in d.get("contents") or []:
            contents_item = ContainerContent.from_dict(contents_item_data)

            contents.append(contents_item)

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

        name = d.get("name")

        parent_storage_id = d.get("parentStorageId")

        parent_storage_schema = None
        if d.get("parentStorageSchema") is not None:
            parent_storage_schema = SchemaSummary.from_dict(cast(Dict[str, Any], d.get("parentStorageSchema")))

        project_id = d.get("projectId")

        schema = None
        if d.get("schema") is not None:
            schema = SchemaSummary.from_dict(cast(Dict[str, Any], d.get("schema")))

        volume = None
        if d.get("volume") is not None:
            volume = d.get("volume")

        web_url = d.get("webURL")

        return Well(
            barcode=barcode,
            contents=contents,
            created_at=created_at,
            creator=creator,
            fields=fields,
            id=id,
            modified_at=modified_at,
            name=name,
            parent_storage_id=parent_storage_id,
            parent_storage_schema=parent_storage_schema,
            project_id=project_id,
            schema=schema,
            volume=volume,
            web_url=web_url,
        )
