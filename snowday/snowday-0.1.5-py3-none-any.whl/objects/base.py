from dataclasses import dataclass
from snowday.exceptions import InvalidWhitespaceException
from snowday.util import get_resource_type, settings_str_from
from snowday.types.base import Sql


@dataclass
class BaseSnowflakeObject:

    name: str

    def __post_init__(self):
        if " " in self.name:
            raise InvalidWhitespaceException(
                f"Invalid whitespace in name: {self.name}\n\nPlease make it {self.name.replace(' ', '')} instead."
            )
        self.name = self.name.upper()
        if callable(getattr(self, "_validate", None)):
            self._validate()

    @property
    def _settings_str(self):
        return settings_str_from(self)

    @property
    def fqn(self):
        return self.name

    @property
    def resource_type_modifier(self):
        return None

    @property
    def _resource_type_str(self):
        modifier_str = f"{self.resource_type_modifier} "
        return (
            f"{modifier_str if self.resource_type_modifier else ''}{self.resource_type}"
        )

    @property
    def resource_type(self):
        return get_resource_type(self)

    @property
    def describe(self):
        return Sql(statement=f"describe {self.resource_type} {self.fqn};")

    @property
    def drop(self):
        return Sql(statement=f"drop {self.resource_type} {self.fqn};")

    @property
    def drop_if_exists(self):
        return Sql(statement=f"drop {self.resource_type} if exists {self.fqn};")

    @property
    def create(self):
        return Sql(
            statement=(
                f"create {self._resource_type_str} "
                f"{self.fqn} "
                f"{self._settings_str};"
            )
        )

    @property
    def create_if_not_exists(self):
        return Sql(
            statement=(
                f"create {self._resource_type_str} if not exists "
                f"{self.fqn} "
                f"{self._settings_str};"
            )
        )

    @property
    def create_or_replace(self):
        return Sql(
            statement=(
                f"create or replace {self._resource_type_str} "
                f"{self.fqn} "
                f"{self._settings_str};"
            )
        )

    def __str__(self):
        return self.fqn
