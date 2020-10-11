from typing import Union, List
from magicdb import db, ASCENDING, DESCENDING, DocumentSnapshot
from magicdb.utils.Serverless.span import safe_span

import time


class Query:
    def __init__(self, cls):
        from magicdb.Models.MagicModel import MagicModel

        self.cls: MagicModel = cls
        self.collection_path = self.cls.get_collection_name()
        self.firebase_query = self.create_query()
        self.query_inputs: List[str] = []

    def create_query(self):
        self.firebase_query = db.conn.collection(self.collection_path)
        return self.firebase_query

    def parent(self, parent_or_path):
        from magicdb.Models.MagicModel import MagicModel

        parent_path = (
            parent_or_path
            if not issubclass(type(parent_or_path), MagicModel)
            else parent_or_path.key
        )

        self.collection_path = parent_path + "/" + self.collection_path
        self.create_query()
        return self

    def document(self, document_path):
        self.firebase_query = self.firebase_query.document(document_path)
        return self

    def collection_group(self):
        self.firebase_query = db.conn.collection_group(self.cls.get_collection_name())
        return self

    def collection(self, collection_path):
        self.firebase_query = self.firebase_query.collection(collection_path)
        return self

    """Wrapping Firestore abilities."""

    def where(self, field, action, value):
        self.firebase_query = self.firebase_query.where(field, action, value)
        self.query_inputs.append(f"{field}, {action}, {value}")
        return self

    def order_by(self, field, direction=None, **kwargs):
        if direction:
            kwargs["direction"] = direction
        if kwargs.get("direction", None) == "asc":
            kwargs["direction"] = ASCENDING
        if kwargs.get("direction", None) == "desc":
            kwargs["direction"] = DESCENDING
        self.firebase_query = self.firebase_query.order_by(field, **kwargs)
        return self

    def start_at(self, fields):
        self.firebase_query = self.firebase_query.start_at(fields)
        return self

    def start_after(self, fields):
        self.firebase_query = self.firebase_query.start_after(fields)
        return self

    def end_at(self, fields):
        self.firebase_query = self.firebase_query.end_at(fields)
        return self

    def end_before(self, fields):
        self.firebase_query = self.firebase_query.end_before(fields)
        return self

    def limit(self, limit):
        if not limit:
            print("no limit given")
            return self
        self.firebase_query = self.firebase_query.limit(limit)
        return self

    def get_path_of_query(self):
        if getattr(self.firebase_query, "_path", None):
            return "/".join(self.firebase_query._path)
        if getattr(self.firebase_query, "_parent", None):
            return "/".join(self.firebase_query._parent._path)
        else:
            return self.collection_path

    """Querying and creating of the models."""

    def make_safe_span_label(self, query_type):
        return f"{query_type}-{self.get_path_of_query()}-{str(self.query_inputs)}"

    def stream(self, validate_db_data=True, **kwargs):
        """Currently defaults to validating the db data, but you can turn this off with the validate_db_data param"""
        with safe_span(self.make_safe_span_label("stream")):
            docs = list(self.firebase_query.stream(**kwargs))

        constructor = self.cls if validate_db_data else self.cls.construct

        return [
            constructor(from_db=True, doc=doc, **doc.to_dict(), key=doc.reference.path)
            for doc in docs
        ]

    def get(self, id=None, create=False, validate_db_data=True, **kwargs):
        if id:
            self.firebase_query = self.firebase_query.document(id)

        with safe_span(self.make_safe_span_label("get")):
            doc = self.firebase_query.get(**kwargs)

        if type(doc) != DocumentSnapshot:
            return None

        d = doc.to_dict()
        if not d:
            return None if not create else self.cls(id=id)

        constructor = self.cls if validate_db_data else self.cls.construct

        return constructor(
            from_db=True, doc=doc, **doc.to_dict(), key=doc.reference.path,
        )

    def get_all(self, ids, validate_db_data=True, **kwargs):
        doc_refs = [db.conn.collection(self.collection_path).document(id) for id in ids]

        with safe_span(self.make_safe_span_label("get_all")):
            docs = db.conn.get_all(doc_refs, **kwargs)

        constructor = self.cls if validate_db_data else self.cls.construct
        return [
            constructor(from_db=True, doc=doc, **doc.to_dict(), key=doc.reference.path,)
            for doc in docs
        ]

    """Subcollections"""

    def collections(self):
        return self.firebase_query.collections()

    def collections_names(self):
        return [coll.id for coll in self.firebase_query.collections()]
