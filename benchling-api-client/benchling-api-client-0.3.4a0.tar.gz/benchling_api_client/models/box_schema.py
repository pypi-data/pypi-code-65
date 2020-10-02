from typing import Any, Dict, List, Optional

import attr

from ..models.schema_field import SchemaField


@attr.s(auto_attribs=True)
class BoxSchema:
    """  """

    height: Optional[float] = None
    width: Optional[float] = None
    container_schema: Optional[Dict[Any, Any]] = None
    id: Optional[str] = None
    name: Optional[str] = None
    field_definitions: Optional[List[SchemaField]] = None
    type: Optional[str] = None
    prefix: Optional[str] = None
    registry_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        height = self.height
        width = self.width
        container_schema = self.container_schema if self.container_schema else None

        id = self.id
        name = self.name
        if self.field_definitions is None:
            field_definitions = None
        else:
            field_definitions = []
            for field_definitions_item_data in self.field_definitions:
                field_definitions_item = field_definitions_item_data.to_dict()

                field_definitions.append(field_definitions_item)

        type = self.type
        prefix = self.prefix
        registry_id = self.registry_id

        return {
            "height": height,
            "width": width,
            "containerSchema": container_schema,
            "id": id,
            "name": name,
            "fieldDefinitions": field_definitions,
            "type": type,
            "prefix": prefix,
            "registryId": registry_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BoxSchema":
        height = d.get("height")

        width = d.get("width")

        container_schema = None
        if d.get("containerSchema") is not None:
            container_schema = d.get("containerSchema")

        id = d.get("id")

        name = d.get("name")

        field_definitions = []
        for field_definitions_item_data in d.get("fieldDefinitions") or []:
            field_definitions_item = SchemaField.from_dict(field_definitions_item_data)

            field_definitions.append(field_definitions_item)

        type = d.get("type")

        prefix = d.get("prefix")

        registry_id = d.get("registryId")

        return BoxSchema(
            height=height,
            width=width,
            container_schema=container_schema,
            id=id,
            name=name,
            field_definitions=field_definitions,
            type=type,
            prefix=prefix,
            registry_id=registry_id,
        )
