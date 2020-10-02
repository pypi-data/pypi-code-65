from typing import Any, Dict, List, Optional

import attr

from ..models.checkout_record import CheckoutRecord
from ..models.container_content import ContainerContent
from ..models.fields import Fields
from ..models.measurement import Measurement
from ..models.user_summary import UserSummary


@attr.s(auto_attribs=True)
class Container:
    """  """

    id: str
    barcode: str
    checkout_record: CheckoutRecord
    created_at: str
    creator: UserSummary
    fields: Fields
    modified_at: str
    name: str
    parent_storage_id: str
    parent_storage_schema: Dict[Any, Any]
    project_id: Optional[str]
    schema: Dict[Any, Any]
    volume: Measurement
    contents: Optional[List[ContainerContent]] = None
    web_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        barcode = self.barcode
        checkout_record = self.checkout_record.to_dict()

        created_at = self.created_at
        creator = self.creator.to_dict()

        fields = self.fields.to_dict()

        modified_at = self.modified_at
        name = self.name
        parent_storage_id = self.parent_storage_id
        parent_storage_schema = self.parent_storage_schema

        project_id = self.project_id
        schema = self.schema

        volume = self.volume.to_dict()

        if self.contents is None:
            contents = None
        else:
            contents = []
            for contents_item_data in self.contents:
                contents_item = contents_item_data.to_dict()

                contents.append(contents_item)

        web_url = self.web_url

        return {
            "id": id,
            "barcode": barcode,
            "checkoutRecord": checkout_record,
            "createdAt": created_at,
            "creator": creator,
            "fields": fields,
            "modifiedAt": modified_at,
            "name": name,
            "parentStorageId": parent_storage_id,
            "parentStorageSchema": parent_storage_schema,
            "projectId": project_id,
            "schema": schema,
            "volume": volume,
            "contents": contents,
            "webURL": web_url,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Container":
        id = d["id"]

        barcode = d["barcode"]

        checkout_record = CheckoutRecord.from_dict(d["checkoutRecord"])

        created_at = d["createdAt"]

        creator = UserSummary.from_dict(d["creator"])

        fields = Fields.from_dict(d["fields"])

        modified_at = d["modifiedAt"]

        name = d["name"]

        parent_storage_id = d["parentStorageId"]

        parent_storage_schema = d["parentStorageSchema"]

        project_id = d["projectId"]

        schema = d["schema"]

        volume = Measurement.from_dict(d["volume"])

        contents = []
        for contents_item_data in d.get("contents") or []:
            contents_item = ContainerContent.from_dict(contents_item_data)

            contents.append(contents_item)

        web_url = d.get("webURL")

        return Container(
            id=id,
            barcode=barcode,
            checkout_record=checkout_record,
            created_at=created_at,
            creator=creator,
            fields=fields,
            modified_at=modified_at,
            name=name,
            parent_storage_id=parent_storage_id,
            parent_storage_schema=parent_storage_schema,
            project_id=project_id,
            schema=schema,
            volume=volume,
            contents=contents,
            web_url=web_url,
        )
