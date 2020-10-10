import copy as cp
from typing import Any, Iterator, Optional

from tdxapi.models.custom_attribute import CustomAttribute


class CustomAttributeList(list):
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = []
        super(CustomAttributeList, self).__init__(iterable)

    def __iter__(self) -> Iterator[CustomAttribute]:
        for attr in super(CustomAttributeList, self).__iter__():
            yield attr

    def __getitem__(self, index) -> CustomAttribute:
        return super(CustomAttributeList, self).__getitem__(index)

    def get(self, attr_id: int, default: Optional[Any] = None) -> CustomAttribute:
        """Retrieve an attribute from list."""
        for attr in self:
            if attr.id == attr_id:
                return attr

        return default

    def get_copy(self, attr_id: int, default: Optional[Any] = None) -> CustomAttribute:
        """Retrieve a copy of an attribute from list."""
        for attr in self:
            if attr.id == attr_id:
                return cp.deepcopy(attr)

        return default

    def update(self, attr_id: int, value: Any) -> None:
        """Update an attribute from list with value."""
        attr = self.get(attr_id)

        if attr is None:
            raise ValueError(f"attribute {attr_id} not in list")

        attr.value = format_attr_value(value)

    def update_copy(self, attr_id: int, value: Any) -> CustomAttribute:
        """Retrieve a copy of an attribute from list with updated value."""
        attr = self.get_copy(attr_id)

        if attr is None:
            raise ValueError(f"attribute {attr_id} not in list")

        attr.value = format_attr_value(value)

        return attr

    def copy(self) -> "CustomAttributeList":
        """Return a copy of list."""
        return cp.deepcopy(self)

    def match_template(self, template: "CustomAttributeList") -> None:
        # Empty template, nothing to do
        if not template:
            return

        existing_ids = [a.id for a in self]

        # Model has some attributes, fill in the missing ones
        for attr in template:
            if attr.id not in existing_ids:
                self.append(cp.deepcopy(attr))

    @classmethod
    def from_data(cls, data):
        return cls(CustomAttribute.from_data(data))


def format_attr_value(value):
    # Attributes that can be searched by multiple values can be specified in a list,
    # but are passed to the api as a comma delimited string i.e. [123, 456] -> "123,456"
    if isinstance(value, (list, tuple)):
        return ",".join(str(v) for v in value)
    else:
        return value
