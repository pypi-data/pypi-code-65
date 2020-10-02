from typing import Any, Dict, Optional

import attr

from ..models.validation_status import ValidationStatus


@attr.s(auto_attribs=True)
class AssayRunCreate:
    """  """

    schema_id: str
    fields: Dict[Any, Any]
    id: Optional[str] = None
    project_id: Optional[str] = None
    validation_status: Optional[ValidationStatus] = None
    validation_comment: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        schema_id = self.schema_id
        fields = self.fields

        id = self.id
        project_id = self.project_id
        validation_status = self.validation_status.value if self.validation_status else None

        validation_comment = self.validation_comment

        return {
            "schemaId": schema_id,
            "fields": fields,
            "id": id,
            "projectId": project_id,
            "validationStatus": validation_status,
            "validationComment": validation_comment,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AssayRunCreate":
        schema_id = d["schemaId"]

        fields = d["fields"]

        id = d.get("id")

        project_id = d.get("projectId")

        validation_status = None
        if d.get("validationStatus") is not None:
            validation_status = ValidationStatus(d.get("validationStatus"))

        validation_comment = d.get("validationComment")

        return AssayRunCreate(
            schema_id=schema_id,
            fields=fields,
            id=id,
            project_id=project_id,
            validation_status=validation_status,
            validation_comment=validation_comment,
        )
