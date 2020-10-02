from typing import Any, Dict, List, Optional

import attr

from ..models.schema_field import SchemaField


@attr.s(auto_attribs=True)
class TagSchema:
    """  """

    constraint: Optional[Dict[Any, Any]] = None
    containable_type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    field_definitions: Optional[List[SchemaField]] = None
    type: Optional[str] = None
    prefix: Optional[str] = None
    registry_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        constraint = self.constraint if self.constraint else None

        containable_type = self.containable_type
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
            "constraint": constraint,
            "containableType": containable_type,
            "id": id,
            "name": name,
            "fieldDefinitions": field_definitions,
            "type": type,
            "prefix": prefix,
            "registryId": registry_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "TagSchema":
        constraint = None
        if d.get("constraint") is not None:
            constraint = d.get("constraint")

        containable_type = d.get("containableType")

        id = d.get("id")

        name = d.get("name")

        field_definitions = []
        for field_definitions_item_data in d.get("fieldDefinitions") or []:
            field_definitions_item = SchemaField.from_dict(field_definitions_item_data)

            field_definitions.append(field_definitions_item)

        type = d.get("type")

        prefix = d.get("prefix")

        registry_id = d.get("registryId")

        return TagSchema(
            constraint=constraint,
            containable_type=containable_type,
            id=id,
            name=name,
            field_definitions=field_definitions,
            type=type,
            prefix=prefix,
            registry_id=registry_id,
        )
