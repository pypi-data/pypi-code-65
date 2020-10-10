import json
from abc import ABC, abstractmethod

import falcon

from .authorize import Authorize
from ._schemas import _NoSchema


def abstractproperty(func):
    return property(classmethod(abstractmethod(func)))


class FirstoreBaseResource(ABC):
    schema_in = _NoSchema
    schema_out = _NoSchema
    schema_ud = _NoSchema
    schema_q = _NoSchema
    allowed = None

    @abstractproperty
    def collection(cls):
        return NotImplementedError

    @falcon.before(Authorize("on_get"))
    def on_get(self, req, resp):
        try:
            query = self.collection
            print(req.params)

            if req.params:
                params = self.schema_q.parse_obj(req.params)

                if params.order_by:
                    query = query.order_by(
                        field_path=params.order_by, direction=params.order_dir
                    )

            docs = query.get()
            validated = [self.schema_out(doc.to_dict()).dict() for doc in docs]

            resp.status = falcon.HTTP_200
            resp.media = validated

        except Exception as e:
            raise falcon.HTTPBadRequest(title="Unknown Error")

    @falcon.before(Authorize("on_get_id"))
    def on_get_id(self, req, resp, id):
        try:
            doc = self.collection.document(id).get()
            validated = self.schema_out.parse_obj(doc.to_dict())

            resp.status = falcon.HTTP_200
            resp.body = validated.json()

        except Exception as e:
            raise falcon.HTTPBadRequest(title="Unknown Error")

    @falcon.before(Authorize("on_post"))
    def on_post(self, req, resp):
        try:
            doc_ref = self.collection.document()

            validated = self.schema_in.parse_obj(req.media)

            doc = doc_ref.set({"id": doc_ref.id, **validated.dict()})

            resp.status = falcon.HTTP_201
            resp.body = validated.json()

        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(title="Unknown Error Resource")

    @falcon.before(Authorize("on_put_id"))
    def on_put_id(self, req, resp, id):
        try:
            validated = self.schema_ud.parse_obj(req.media)

            doc_ref = self.collection.document(id)
            doc = doc_ref.update(validated.dict())

            resp.status = falcon.HTTP_200
            resp.body = validated.json()

        except Exception as e:
            raise falcon.HTTPBadRequest(title="Unknown Error")

    @falcon.before(Authorize("on_delete_id"))
    def on_delete_id(self, req, resp, id):
        try:
            self.collection.document(id).delete()
            resp.status = falcon.HTTP_200

        except Exception as e:
            raise falcon.HTTPBadRequest(title="Unknown Error")
