from __future__ import annotations
import threading
from typing import List, Dict, Any

import concurrent.futures


import copy
import time
import pprint

import magicdb
from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from magicdb.Models import model_helpers
from magicdb.Queries import Query
from magicdb.utils.Serverless.span import safe_span

from magicdb.utils.updating_objects import make_update_obj

MAGIC_FIELDS = ["id", "key", "ref", "parent", "kwargs_from_db", "doc"]

# ref will break this cause it is not jsonable
MAGIC_FIELDS_TO_EXCLUDE = set(MAGIC_FIELDS) - {"id"}

FIELDS_TO_EXCLUDE_FOR_DB = set(MAGIC_FIELDS)


class DatabaseError(Exception):
    def __init__(self, key):
        self.message = (
            f"There is no document with key {key} to update. Add update.(create=True) to save the document"
            f" if it does not exist. Otherwise, you can save the document: save()."
        )


class QueryMeta(type):
    """https://stackoverflow.com/questions/128573/using-property-on-classmethods"""

    @property
    def collection(cls) -> Query:
        return Query(cls)

    @property
    def collection_group(cls) -> Query:
        return Query(cls).collection_group()


class QueryAndBaseMetaClasses(ModelMetaclass, QueryMeta):
    pass


class MagicModel(BaseModel, metaclass=QueryAndBaseMetaClasses):
    """
    When this gets inited, if given an id or key, assign based on that.
    Otherwise, assign them based on what Firestore gives it
    """

    id: str = None
    key: str = None
    # ref: magicdb.DocumentReference = None
    # doc: magicdb.DocumentSnapshot = None
    ref: Any = None
    doc: Any = None
    parent: MagicModel = None
    kwargs_from_db: dict = None

    __call__ = ...  # to satisfy Query python linter

    def __init__(self, from_db: bool = False, **kwargs):
        """Feed in all magic fields as kwargs"""
        kwargs_copy = kwargs.copy()
        model_helpers.make_magic_fields_from_kwargs(
            kwargs=kwargs, collection_name=self.collection_name
        )
        super().__init__(**kwargs)
        self.kwargs_from_db = {} if not from_db else kwargs_copy

    @classmethod
    def construct(cls, *args, from_db: bool = False, **kwargs):
        kwargs_copy = kwargs.copy()
        model_helpers.make_magic_fields_from_kwargs(
            kwargs=kwargs, collection_name=cls.get_collection_name()
        )
        new_obj = super().construct(*args, **kwargs)
        new_obj.kwargs_from_db = {} if not from_db else kwargs_copy
        return new_obj

    """GETTING AND SETTING FIELDS"""

    def set_id(self, id: str):
        kwargs = {"id": id}
        model_helpers.make_magic_fields_from_id_parent_or_nothing(
            kwargs=kwargs, collection_name=self.collection_name
        )
        self.__dict__.update(kwargs)

    def set_key(self, key: str):
        kwargs = {"key": key}
        model_helpers.make_magic_fields_from_key(kwargs=kwargs)
        self.__dict__.update(kwargs)

    def set_ref(self, ref: magicdb.DocumentReference):
        kwargs = {"ref": ref}
        model_helpers.make_magic_fields_from_ref(kwargs=kwargs)
        self.__dict__.update(kwargs)

    def set_parent(self, parent: MagicModel):
        kwargs = {"parent": parent}
        model_helpers.make_magic_fields_from_id_parent_or_nothing(
            kwargs=kwargs, collection_name=self.collection_name
        )
        self.__dict__.update(kwargs)

    """OVERRIDING PYDANTIC"""

    @classmethod
    def get_fields_to_exclude(cls):
        return getattr(cls.Meta, "magic_fields_to_exclude", MAGIC_FIELDS_TO_EXCLUDE)

    def dict(self, *args, exclude_magic_fields=True, **kwargs):
        to_exclude = set() if not exclude_magic_fields else self.get_fields_to_exclude()
        # join w other fields passed in
        kwargs["exclude"] = kwargs.get("exclude") or set() | to_exclude
        return super().dict(*args, **kwargs)

    @classmethod
    def schema(cls, *args, **kwargs):
        """Temporarily take out the excluded fields to get the schema, then put them back."""

        original_fields = cls.__fields__.copy()

        for magic_field in cls.get_fields_to_exclude():
            if magic_field in cls.__fields__:
                del cls.__fields__[magic_field]

        schema_d = super().schema(*args, **kwargs)

        # cannot set __fields__ directly so will remove all items then update the d w the original fields
        for key in list(cls.__fields__.keys()):
            del cls.__fields__[key]

        cls.__fields__.update(original_fields)
        return schema_d

    """META CLASS FUNCTIONS"""

    @property
    def collection_name(self) -> str:
        return self.get_collection_name()

    @classmethod
    def make_default_collection_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def get_collection_name(cls) -> str:
        return getattr(cls.Meta, "collection_name", cls.make_default_collection_name())

    """PRINTING AND RETURNING"""

    def __repr__(self, *args, **kwargs):
        return f"{self.__class__.__name__}({self.__repr_str__(', ')})"

    def __str__(self, *args, **kwargs):
        return f"{self.__repr_str__(' ')}"

    def __repr_str__(self, join_str=", ", fields_to_exclude: set = None):
        fields_to_exclude: set = (
            fields_to_exclude
            if fields_to_exclude is not None
            else self.get_fields_to_exclude()
        )
        key_values: List[str] = []
        for field in self.__dict__:
            if field not in fields_to_exclude:
                key_values.append(f"{repr(field)}={repr(getattr(self, field, None))}")
        return join_str.join(key_values)

    def print_all(self):
        result: str = self.__repr_str__(fields_to_exclude=set())
        print("PRINT_ALL", result)
        return result

    class Meta:
        """Init the meta class so you can use it and know it is there"""

        """Looks like having Meta in the TestModel actually overrites this one, not inherits it"""
        ...

    class Serverless:
        """Fills this with the latest context if it exists"""

        context = None

    class Config:
        anystr_strip_whitespace: bool = True

        arbitrary_types_allowed: bool = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: MagicModel) -> None:
            keys = list(schema.get("properties", {}).keys())
            to_exclude = model.get_fields_to_exclude()
            for key in keys:
                if key in to_exclude:
                    schema.get("properties", {}).pop(key)

        json_encoders = {magicdb.DocumentReference: lambda doc_ref: doc_ref.path}

    """ADDING TO FIRESTORE"""

    @staticmethod
    def remove_magic_fields(d):
        for magic_field in MAGIC_FIELDS:
            if magic_field in d:
                del d[magic_field]
        return d

    def save(self, batch=None, merge=False, ignore_fields=False):
        """Will create a new obj_to_save and save it so that all of the validation happens properly on a new obj."""
        obj_to_save = (
            self
            if ignore_fields
            else self.__class__(**self.dict(exclude_magic_fields=False))
        )
        new_d = obj_to_save.dict()
        self.remove_magic_fields(new_d)

        with safe_span(f"save-{self.key}", use=(batch is None)):
            obj_to_save.ref.set(new_d, merge=merge) if not batch else batch.set(
                obj_to_save.ref, new_d, merge=merge
            )
        if not merge:
            obj_to_save.kwargs_from_db = copy.deepcopy(new_d)

        # update self just in case
        self.__dict__.update(obj_to_save.__dict__)
        return obj_to_save

    def update(self, batch=None, create=False, ignore_fields=False):
        obj_to_update = (
            self
            if ignore_fields
            else self.__class__(**self.dict(exclude_magic_fields=False))
        )
        new_d = obj_to_update.dict()

        self.remove_magic_fields(new_d)

        self.get_fields_to_exclude()
        update_d = (
            new_d
            if not obj_to_update.kwargs_from_db
            else make_update_obj(original=obj_to_update.kwargs_from_db, new=new_d)
        )

        try:
            with safe_span(f"update-{self.key}", use=(batch is None)):
                obj_to_update.ref.update(update_d) if not batch else batch.update(
                    obj_to_update.ref, update_d
                )
            self.__dict__.update(obj_to_update.__dict__)
            return obj_to_update
        except Exception as e:
            if hasattr(e, "message") and "no document to update" in e.message.lower():
                if create:
                    return obj_to_update.save(batch=batch)
                else:
                    db_error = DatabaseError(obj_to_update.key)
                    raise DatabaseError(db_error.message)

    def delete(self, batch=None):
        with safe_span(f"delete-{self.key}", use=(batch is None)):
            return self.ref.delete() if not batch else batch.delete(self.ref)

    """Writing to DB async"""

    def save_async(self, *args, **kwargs) -> threading.Thread:
        t = threading.Thread(target=self.save, args=(*args,), kwargs={**kwargs})
        t.start()
        return t

    def update_async(self, *args, **kwargs) -> threading.Thread:
        t = threading.Thread(target=self.update, args=(*args,), kwargs={**kwargs})
        t.start()
        return t

    def delete_async(self, *args, **kwargs) -> threading.Thread:
        t = threading.Thread(target=self.delete, args=(*args,), kwargs={**kwargs})
        t.start()
        return t

    """QUERYING AND COLLECTIONS"""

    def exists(self):
        return self.__class__.collection.get(self.id) is not None

    def get_subcollections(self):
        return list(self.__class__.collection.document(self.id).collections())

    """GETTING SUBCLASSES"""

    @classmethod
    def get_subclasses(cls):
        all_subs = []
        for sub in cls.__subclasses__():
            all_subs.append(sub)
            all_subs += sub.get_subclasses()
        return list(set(all_subs))

    @staticmethod
    def get_all_subclasses_of_model():
        all_subs = []
        for sub in list(MagicModel.__subclasses__()):
            all_subs.append(sub)
            all_subs += sub.get_subclasses()
        return list(set(all_subs))

    @staticmethod
    def stream_queries(queries: List[magicdb.Query]):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # set this to 10 because lambda only has 2 cores so would only have 6 threads for max_workers
            executor._max_workers = max(executor._max_workers, 20)
            futures = [
                executor.submit(
                    query.stream,
                )
                for query in queries
            ]
            return [f.result() for f in futures]


MagicModel.update_forward_refs()
