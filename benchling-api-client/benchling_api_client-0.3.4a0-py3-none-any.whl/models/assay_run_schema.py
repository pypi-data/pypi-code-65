from typing import Any, Dict, List, Optional

import attr

from ..models.schema_field import SchemaField
from ..models.type import Type


@attr.s(auto_attribs=True)
class AssayRunSchema:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    field_definitions: Optional[List[SchemaField]] = None
    type: Optional[Type] = None
    system_name: Optional[str] = None
    derived_from: Optional[str] = None
    automation_input_file_configs: Optional[List[Dict[Any, Any]]] = None
    automation_output_file_configs: Optional[List[Dict[Any, Any]]] = None
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
        derived_from = self.derived_from
        if self.automation_input_file_configs is None:
            automation_input_file_configs = None
        else:
            automation_input_file_configs = []
            for automation_input_file_configs_item_data in self.automation_input_file_configs:
                automation_input_file_configs_item = automation_input_file_configs_item_data

                automation_input_file_configs.append(automation_input_file_configs_item)

        if self.automation_output_file_configs is None:
            automation_output_file_configs = None
        else:
            automation_output_file_configs = []
            for automation_output_file_configs_item_data in self.automation_output_file_configs:
                automation_output_file_configs_item = automation_output_file_configs_item_data

                automation_output_file_configs.append(automation_output_file_configs_item)

        organization = self.organization if self.organization else None

        return {
            "id": id,
            "name": name,
            "fieldDefinitions": field_definitions,
            "type": type,
            "systemName": system_name,
            "derivedFrom": derived_from,
            "automationInputFileConfigs": automation_input_file_configs,
            "automationOutputFileConfigs": automation_output_file_configs,
            "organization": organization,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AssayRunSchema":
        id = d.get("id")

        name = d.get("name")

        field_definitions = []
        for field_definitions_item_data in d.get("fieldDefinitions") or []:
            field_definitions_item = SchemaField.from_dict(field_definitions_item_data)

            field_definitions.append(field_definitions_item)

        type = None
        if d.get("type") is not None:
            type = Type(d.get("type"))

        system_name = d.get("systemName")

        derived_from = d.get("derivedFrom")

        automation_input_file_configs = []
        for automation_input_file_configs_item_data in d.get("automationInputFileConfigs") or []:
            automation_input_file_configs_item = automation_input_file_configs_item_data

            automation_input_file_configs.append(automation_input_file_configs_item)

        automation_output_file_configs = []
        for automation_output_file_configs_item_data in d.get("automationOutputFileConfigs") or []:
            automation_output_file_configs_item = automation_output_file_configs_item_data

            automation_output_file_configs.append(automation_output_file_configs_item)

        organization = None
        if d.get("organization") is not None:
            organization = d.get("organization")

        return AssayRunSchema(
            id=id,
            name=name,
            field_definitions=field_definitions,
            type=type,
            system_name=system_name,
            derived_from=derived_from,
            automation_input_file_configs=automation_input_file_configs,
            automation_output_file_configs=automation_output_file_configs,
            organization=organization,
        )
