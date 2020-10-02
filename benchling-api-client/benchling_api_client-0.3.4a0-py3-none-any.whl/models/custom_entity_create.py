from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class CustomEntityCreate:
    """  """

    author_ids: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    custom_fields: Optional[Dict[Any, Any]] = None
    fields: Optional[Dict[Any, Any]] = None
    folder_id: Optional[str] = None
    name: Optional[str] = None
    schema_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.author_ids is None:
            author_ids = None
        else:
            author_ids = self.author_ids

        if self.aliases is None:
            aliases = None
        else:
            aliases = self.aliases

        custom_fields = self.custom_fields if self.custom_fields else None

        fields = self.fields if self.fields else None

        folder_id = self.folder_id
        name = self.name
        schema_id = self.schema_id

        return {
            "authorIds": author_ids,
            "aliases": aliases,
            "customFields": custom_fields,
            "fields": fields,
            "folderId": folder_id,
            "name": name,
            "schemaId": schema_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "CustomEntityCreate":
        author_ids = d.get("authorIds")

        aliases = d.get("aliases")

        custom_fields = None
        if d.get("customFields") is not None:
            custom_fields = d.get("customFields")

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        folder_id = d.get("folderId")

        name = d.get("name")

        schema_id = d.get("schemaId")

        return CustomEntityCreate(
            author_ids=author_ids,
            aliases=aliases,
            custom_fields=custom_fields,
            fields=fields,
            folder_id=folder_id,
            name=name,
            schema_id=schema_id,
        )
