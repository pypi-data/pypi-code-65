from typing import Any, Dict, List, Optional

import attr

from ..models.schema_field import SchemaField
from ..models.type12 import Type12


@attr.s(auto_attribs=True)
class RequestSchema:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    field_definitions: Optional[List[SchemaField]] = None
    type: Optional[Type12] = None
    system_name: Optional[str] = None
    organization: Optional[Dict[Any, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        if self.field_definitions is None:
            field_definitions = None
        else:
            field_definitions = []
            for field_definitions_item_data in self.field_definitions:
                field_definitions_item = field_definitions_item_data.to_dict()

                field_definitions.append(field_definitions_item)

        type = self.type.value if self.type else None

        system_name = self.system_name
        organization = self.organization if self.organization else None

        return {
            "id": id,
            "name": name,
            "fieldDefinitions": field_definitions,
            "type": type,
            "systemName": system_name,
            "organization": organization,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RequestSchema":
        id = d.get("id")

        name = d.get("name")

        field_definitions = []
        for field_definitions_item_data in d.get("fieldDefinitions") or []:
            field_definitions_item = SchemaField.from_dict(field_definitions_item_data)

            field_definitions.append(field_definitions_item)

        type = None
        if d.get("type") is not None:
            type = Type12(d.get("type"))

        system_name = d.get("systemName")

        organization = None
        if d.get("organization") is not None:
            organization = d.get("organization")

        return RequestSchema(
            id=id,
            name=name,
            field_definitions=field_definitions,
            type=type,
            system_name=system_name,
            organization=organization,
        )
