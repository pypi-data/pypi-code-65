from typing import Any, Dict, List, Optional

import attr

from ..models.annotation import Annotation
from ..models.primer import Primer
from ..models.translation import Translation


@attr.s(auto_attribs=True)
class DnaSequencePatch:
    """  """

    entity_registry_id: Optional[str] = None
    author_ids: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    annotations: Optional[List[Annotation]] = None
    bases: Optional[str] = None
    custom_fields: Optional[Dict[Any, Any]] = None
    fields: Optional[Dict[Any, Any]] = None
    folder_id: Optional[str] = None
    is_circular: Optional[bool] = None
    name: Optional[str] = None
    primers: Optional[List[Primer]] = None
    schema_id: Optional[str] = None
    translations: Optional[List[Translation]] = None

    def to_dict(self) -> Dict[str, Any]:
        entity_registry_id = self.entity_registry_id
        if self.author_ids is None:
            author_ids = None
        else:
            author_ids = self.author_ids

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

        bases = self.bases
        custom_fields = self.custom_fields if self.custom_fields else None

        fields = self.fields if self.fields else None

        folder_id = self.folder_id
        is_circular = self.is_circular
        name = self.name
        if self.primers is None:
            primers = None
        else:
            primers = []
            for primers_item_data in self.primers:
                primers_item = primers_item_data.to_dict()

                primers.append(primers_item)

        schema_id = self.schema_id
        if self.translations is None:
            translations = None
        else:
            translations = []
            for translations_item_data in self.translations:
                translations_item = translations_item_data.to_dict()

                translations.append(translations_item)

        return {
            "entityRegistryId": entity_registry_id,
            "authorIds": author_ids,
            "aliases": aliases,
            "annotations": annotations,
            "bases": bases,
            "customFields": custom_fields,
            "fields": fields,
            "folderId": folder_id,
            "isCircular": is_circular,
            "name": name,
            "primers": primers,
            "schemaId": schema_id,
            "translations": translations,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DnaSequencePatch":
        entity_registry_id = d.get("entityRegistryId")

        author_ids = d.get("authorIds")

        aliases = d.get("aliases")

        annotations = []
        for annotations_item_data in d.get("annotations") or []:
            annotations_item = Annotation.from_dict(annotations_item_data)

            annotations.append(annotations_item)

        bases = d.get("bases")

        custom_fields = None
        if d.get("customFields") is not None:
            custom_fields = d.get("customFields")

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        folder_id = d.get("folderId")

        is_circular = d.get("isCircular")

        name = d.get("name")

        primers = []
        for primers_item_data in d.get("primers") or []:
            primers_item = Primer.from_dict(primers_item_data)

            primers.append(primers_item)

        schema_id = d.get("schemaId")

        translations = []
        for translations_item_data in d.get("translations") or []:
            translations_item = Translation.from_dict(translations_item_data)

            translations.append(translations_item)

        return DnaSequencePatch(
            entity_registry_id=entity_registry_id,
            author_ids=author_ids,
            aliases=aliases,
            annotations=annotations,
            bases=bases,
            custom_fields=custom_fields,
            fields=fields,
            folder_id=folder_id,
            is_circular=is_circular,
            name=name,
            primers=primers,
            schema_id=schema_id,
            translations=translations,
        )
