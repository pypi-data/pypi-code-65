from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class AssayRun:
    """  """

    id: Optional[str] = None
    created_at: Optional[str] = None
    schema: Optional[Dict[Any, Any]] = None
    fields: Optional[Dict[Any, Any]] = None
    is_reviewed: Optional[bool] = None
    validation_schema: Optional[str] = None
    validation_comment: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        created_at = self.created_at
        schema = self.schema if self.schema else None

        fields = self.fields if self.fields else None

        is_reviewed = self.is_reviewed
        validation_schema = self.validation_schema
        validation_comment = self.validation_comment

        return {
            "id": id,
            "createdAt": created_at,
            "schema": schema,
            "fields": fields,
            "isReviewed": is_reviewed,
            "validationSchema": validation_schema,
            "validationComment": validation_comment,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AssayRun":
        id = d.get("id")

        created_at = d.get("createdAt")

        schema = None
        if d.get("schema") is not None:
            schema = d.get("schema")

        fields = None
        if d.get("fields") is not None:
            fields = d.get("fields")

        is_reviewed = d.get("isReviewed")

        validation_schema = d.get("validationSchema")

        validation_comment = d.get("validationComment")

        return AssayRun(
            id=id,
            created_at=created_at,
            schema=schema,
            fields=fields,
            is_reviewed=is_reviewed,
            validation_schema=validation_schema,
            validation_comment=validation_comment,
        )
