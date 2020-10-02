import datetime
from typing import Any, Dict, List, Optional, cast

import attr
from dateutil.parser import isoparse

from ..models.annotation import Annotation
from ..models.archive_record import ArchiveRecord
from ..models.primer import Primer
from ..models.schema_summary import SchemaSummary
from ..models.translation import Translation
from ..models.user_summary import UserSummary


@attr.s(auto_attribs=True)
class DnaSequence:
    """  """

    aliases: Optional[List[str]] = None
    annotations: Optional[List[Annotation]] = None
    archive_record: Optional[ArchiveRecord] = None
    bases: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    creator: Optional[UserSummary] = None
    custom_fields: Optional[Dict[Any, Any]] = None
    entity_registry_id: Optional[str] = None
    fields: Optional[Dict[Any, Any]] = None
    folder_id: Optional[str] = None
    id: Optional[str] = None
    is_circular: Optional[bool] = None
    length: Optional[int] = None
    modified_at: Optional[datetime.datetime] = None
    name: Optional[str] = None
    primers: Optional[List[Primer]] = None
    registry_id: Optional[str] = None
    schema: Optional[SchemaSummary] = None
    translations: Optional[List[Translation]] = None
    web_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.aliases is None:
            aliases = None
        else:
            aliases = self.aliases

        if self.annotations is None:
            annotations = None
        else:
            annotations = []
            for annotations_item_data in self.annotations:
                annotations_item = annotations_item_data.to_dict()

                annotations.append(annotations_item)

        archive_record = self.archive_record.to_dict() if self.archive_record else None

        bases = self.bases
        created_at = self.created_at.isoformat() if self.created_at else None

        creator = self.creator.to_dict() if self.creator else None

        custom_fields = self.custom_fields if self.custom_fields else None

        entity_registry_id = self.entity_registry_id
        fields = self.fields if self.fields else None

        folder_id = self.folder_id
        id = self.id
        is_circular = self.is_circular
        length = self.length
        modified_at = self.modified_at.isoformat() if self.modified_at else None

        name = self.name
        if self.primers is None:
            primers = None
        else:
            primers = []
            for primers_item_data in self.primers:
                primers_item = primers_item_data.to_dict()

                primers.append(primers_item)

        registry_id = self.registry_id
        schema = self.schema.to_dict() if self.schema else None

        if self.translations is None:
            translations = None
        else:
            translations = []
            for translations_item_data in self.translations:
                translations_item = translations_item_data.to_dict()

                translations.append(translations_item)

        web_url = self.web_url

        return {
            "aliases": aliases,
            "annotations": annotations,
            "archiveRecord": archive_record,
            "bases": bases,
            "createdAt": created_at,
            "creator": creator,
            "customFields": custom_fields,
            "entityRegistryId": entity_registry_id,
            "fields": fields,
            "folderId": folder_id,
            "id": id,
            "isCircular": is_circular,
            "length": length,
            "modifiedAt": modified_at,
            "name": name,
            "primers": primers,
            "registryId": registry_id,
            "schema": schema,
            "translations": translations,
            "webURL": web_url,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DnaSequence":
        aliases = d.get("aliases")

        annotations = []
        for annotations_item_data in d.get("annotations") or []:
            annotations_item = Annotation.from_dict(annotations_item_data)

            annotations.append(annotations_item)

        archive_record = None
        if d.get("archiveRecord") is not None:
            archive_record = ArchiveRecord.from_dict(cast(Dict[str, Any], d.get("archiveRecord")))

        bases = d.get("bases")

        created_at = None
        if d.get("createdAt") is not None:
            created_at = isoparse(cast(str, d.get("createdAt")))

        creator = None
        if d.get("creator") is not None:
            creator = UserSummary.from_dict(cast(Dict[str, Any], d.get("creator")))

        custom_fields = None
        if d.get("customFields") is not None:
            custom_fields = d.get("customFields")

        entity_registry_id = d.get("entityRegistryId")

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        folder_id = d.get("folderId")

        id = d.get("id")

        is_circular = d.get("isCircular")

        length = d.get("length")

        modified_at = None
        if d.get("modifiedAt") is not None:
            modified_at = isoparse(cast(str, d.get("modifiedAt")))

        name = d.get("name")

        primers = []
        for primers_item_data in d.get("primers") or []:
            primers_item = Primer.from_dict(primers_item_data)

            primers.append(primers_item)

        registry_id = d.get("registryId")

        schema = None
        if d.get("schema") is not None:
            schema = SchemaSummary.from_dict(cast(Dict[str, Any], d.get("schema")))

        translations = []
        for translations_item_data in d.get("translations") or []:
            translations_item = Translation.from_dict(translations_item_data)

            translations.append(translations_item)

        web_url = d.get("webURL")

        return DnaSequence(
            aliases=aliases,
            annotations=annotations,
            archive_record=archive_record,
            bases=bases,
            created_at=created_at,
            creator=creator,
            custom_fields=custom_fields,
            entity_registry_id=entity_registry_id,
            fields=fields,
            folder_id=folder_id,
            id=id,
            is_circular=is_circular,
            length=length,
            modified_at=modified_at,
            name=name,
            primers=primers,
            registry_id=registry_id,
            schema=schema,
            translations=translations,
            web_url=web_url,
        )
