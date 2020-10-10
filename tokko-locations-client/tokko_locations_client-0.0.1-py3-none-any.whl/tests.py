from dataclasses import dataclass
from typing import Any
import unittest
from tokko_locations_client.exceptions import (
    UnsupportedClassError,
    APIConnectionError,
    DataNotFoundError,
    MethodCallError,
    Error
)
from tokko_locations_client.models import (
    AutoSerializerMixin,
    Location,
    Division,
    Country,
    State,

)


class DummySerializableDataclass(AutoSerializerMixin):
    key: str = "DefaultKey"
    value: Any = None


class ModelsTestCases(unittest.TestCase):

    def test_serialize_dataclass(self):
        dummy = dataclass(DummySerializableDataclass)(**{"key": "Hello", "value": "World"})
        self.assertDictEqual(dummy.json, {"key": "Hello", "value": "World"})
        self.assertEqual(dummy.key, "Hello")
        self.assertEqual(dummy.value, "World")

    def test_class_must_be_an_dataclass(self):
        with self.assertRaises(UnsupportedClassError):
            print(f"Never printed: {DummySerializableDataclass().json}")


class ModelsCountryTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.country_json = {
            "id": 1,
            "iso_code": "AR",
            "name": "Argentina",
            "resource_uri": "/api/v1/country/1/",
            "states": [
                # Chunk
                {
                    "id": 146,
                    "name": "Capital Federal",
                    "resource_uri": "/api/v1/state/146/"
                }
            ]
        }

    def test_create_country_model_json(self):
        country = Country(**self.country_json)
        self.assertEqual(country.json["id"], self.country_json["id"])
        self.assertEqual(country.json["iso_code"], self.country_json["iso_code"])
        self.assertEqual(country.json["name"], self.country_json["name"])
        self.assertEqual(country.json["resource_uri"], self.country_json["resource_uri"])
        self.assertEqual(country.json["states"][0]["id"], self.country_json["states"][0]["id"])
        self.assertEqual(country.json["states"][0]["name"], self.country_json["states"][0]["name"])
        self.assertEqual(country.json["states"][0]["resource_uri"], self.country_json["states"][0]["resource_uri"])

    def test_create_country_model_raw(self):
        country = Country(**self.country_json)
        self.assertTrue(country.resource_uri, self.country_json["resource_uri"])
        self.assertTrue(country.id, self.country_json["id"])
        self.assertTrue(country.name, self.country_json["name"])
        self.assertTrue(all([isinstance(state, State) for state in country.states]))
        self.assertTrue(len(country.states) == 1)


class ModelsStateTestCase(unittest.TestCase):
    ...


class ModelsLocationTestCase(unittest.TestCase):
    ...


class ModelsDivisionTestCase(unittest.TestCase):
    ...
