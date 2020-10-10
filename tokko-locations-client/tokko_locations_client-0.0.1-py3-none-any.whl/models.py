from dataclasses import dataclass, fields, is_dataclass
from contextlib import suppress
from typing import List, Union

from tokko_locations_client.exceptions import UnsupportedClassError


__all__ = [
    "AutoSerializerMixin",
    "Country",
    "State",
    "Location",
    "Division"
]


class AutoSerializerMixin:
    """Lazy Model serializer"""

    @property
    def json(self):
        def serialize_fields(field):
            value = getattr(self, field.name, None)
            with suppress(AttributeError):
                if isinstance(value, list):
                    value = [obj.json for obj in value]
            return field.name, value

        if not is_dataclass(self):
            raise UnsupportedClassError(f"Class: {type(self).__name__}")
        return {
            key: value
            for key, value in map(serialize_fields, fields(self))
        }


@dataclass(init=True)
class Division(AutoSerializerMixin):
    """Division Model"""
    # Required fields
    id: int
    name: str
    state: str

    # Optional Fields
    resource_uri: str = None
    full_location: str = None
    short_location: str = None
    parent_division: str = None

    def __repr__(self):
        return f"Division({self.name})"


@dataclass(init=True)
class Location(AutoSerializerMixin):
    # Required fields
    id: int
    name: str
    state: str

    # Optional Fields
    resource_uri: str = None
    full_location: str = None
    short_location: str = None
    parent_division: str = None
    divisions: List[Division] = None

    def __repr__(self):
        divisions = f", divisions={self.divisions}" if self.divisions else ""
        return f"Location({self.name}{divisions})"

    def __post_init__(self):
        def load_division(division: dict) -> Location:
            division.update({"state": self.resource_uri})
            return Division(**division)

        if isinstance(self.divisions, list):
            self.divisions = list(map(load_division, self.divisions))


@dataclass(init=True)
class State(AutoSerializerMixin):
    # Required fields
    id: int
    name: str
    resource_uri: str

    # Optional Fields
    country: str = None
    sap_code: str = None
    full_location: str = None
    divisions: List[Location] = None
    breadcrumbs: List[str] = None

    def make_breadcrumbs(self):
        if all([
            isinstance(self.full_location, str),
            self.full_location,
            not self.breadcrumbs
        ]):
            self.breadcrumbs = self.full_location.split(" | ")

    def __repr__(self):
        divisions = f", divisions={self.divisions}" if self.divisions else ""
        return f"State({self.name}{divisions})"

    def __post_init__(self):
        def load_division(division: dict) -> Location:
            division.update({"state": self.resource_uri})
            return Location(**division)

        self.make_breadcrumbs()
        if isinstance(self.divisions, list):
            self.divisions = list(map(load_division, self.divisions))


@dataclass(init=True)
class Country(AutoSerializerMixin):
    # Required fields
    id: int
    name: str
    iso_code: str
    resource_uri: str

    # Optional Fields
    states: List[Union[State, dict]] = None

    def __repr__(self):
        states = f", states={self.states}" if self.states else ""
        return f"Country({self.iso_code.upper()}{states})"

    def __post_init__(self):

        def load_state(state) -> State:
            state.update({"country": self.resource_uri})
            return State(**state)

        if isinstance(self.states, list):
            self.states = list(map(load_state, self.states))
