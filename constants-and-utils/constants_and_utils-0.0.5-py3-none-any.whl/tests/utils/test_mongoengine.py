import json
import datetime
import pytest
from unittest import TestCase

mongoengine = pytest.importorskip("mongoengine")
mongomock = pytest.importorskip("mongomock")
deepdiff = pytest.importorskip("deepdiff")
bson = pytest.importorskip("bson")


"""Installation::
    pip install constants_and_utils["mongoengine"]
"""
from bson import DBRef, ObjectId  # noqa: E402
from mongoengine import connect, disconnect  # noqa: E402
from mongoengine import (  # noqa: E402
    Document,
    StringField,
    IntField,
    ReferenceField,
    ListField,
)
from constants_and_utils.utils.mongoengine import (  # noqa: E402
    JSONEncoder,
    diff_mongo_objects,
)


class TestJsonEncoder(TestCase):

    def get_request(self) -> dict:
        return {
            'data': ObjectId('5e5852593adfb58d0d664847'),
            'data2': DBRef('ref', '5e552f7d175489508fc62fae'),
            'data3': datetime.datetime.strptime('2020-2-1', "%Y-%m-%d"),
            'data4': 'string'
        }

    def test_ok(self):
        request = self.get_request()
        result = JSONEncoder().encode(request)
        expected = ("{\"data\": \"5e5852593adfb58d0d664847\", "
                    "\"data2\": \"DBRef('ref', '5e552f7d175489508fc62fae')\", "
                    "\"data3\": \"2020-02-01 00:00:00\", "
                    "\"data4\": \"string\"}")
        self.assertEqual(result, expected)
        for k, r in json.loads(result).items():
            self.assertIsInstance(r, str)


class TestDiffObjects(TestCase):

    @classmethod
    def setUpClass(cls):
        connect('mongoenginetest', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def test_diff_objects_update_dbref(self):
        class CatSon(Document):
            name = StringField()

        class CatDad(Document):
            name = StringField()

        class Cat(Document):
            name = StringField()
            age = IntField()
            ref = ReferenceField('CatDad', dbref=True)
            refs = ListField(ReferenceField('CatSon', dbref=True))

        cat_dad = CatDad(name='catdad').save()
        cat_son = CatSon(name='catson').save()

        old_cat = Cat(name="Misifu", age=3, ref=cat_dad, refs=[cat_son])
        new_cat = Cat(name="Misifu", age=5, ref=cat_dad)

        record = diff_mongo_objects(old_cat, new_cat)

        self.assertIsInstance(record, dict)

        self.assertIn("root['age']", record.get("values_changed"))
        self.assertIn("iterable_item_removed", record)
        self.assertNotIn("root['name']", record.get("values_changed"))

    def test_diff_objects_not_update(self):
        class Dog(Document):
            sound = StringField()
            decibels = IntField()

        dog = Dog(sound="Guaf", decibels=20)

        record = diff_mongo_objects(dog, dog)

        self.assertIsInstance(record, dict)
        self.assertEqual(record, dict())
