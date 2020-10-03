from dataclasses import dataclass

from snowday.objects.base import BaseSnowflakeObject
from snowday.objects.database import Schema


@dataclass
class SchemaObject(BaseSnowflakeObject):
    schema: Schema
    comment: str

    @property
    def fqn(self):
        return f"{self.schema.fqn}.{self.name}"
