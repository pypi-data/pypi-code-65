import collections
from typing import TYPE_CHECKING, Any, Iterator, overload

import requests

from hyperfoil.utils import extract_response

if TYPE_CHECKING:
    from hyperfoil.client import HyperfoilClient, RestApiClient


class DefaultClient:
    def __init__(self, parent=None, instance_klass=None) -> None:
        self._parent = parent
        self._instance_klass = instance_klass

    @property
    def hyperfoil_client(self) -> 'HyperfoilClient':
        return self.parent.hyperfoil_client

    @property
    def parent(self) -> 'HyperfoilClient':
        return self._parent

    @property
    def rest(self) -> 'RestApiClient':
        return self.parent.rest

    @property
    def url(self) -> str:
        return self.rest.url

    def fetch(self, entity_id: str = "", **kwargs):
        url = self._entity_url(entity_id=entity_id)
        response = self.rest.get(url=url, **kwargs)
        return extract_response(response)

    def _create_instance(self, response: requests.Response, klass=None, client=None):
        client = client or self
        klass = klass or self._instance_klass
        extracted = extract_response(response)
        if 'text/vnd.yaml' in response.headers.get("Content-Type", ""):
            return klass(client=client, entity=extracted, content_type='text/vnd.yaml') if klass else extracted

        return klass(client=client, entity=extracted, content_type='application/json')

    def _entity_url(self, entity_id: str):
        if not entity_id:
            return self.url
        return self.url + '/' + entity_id


class DefaultResource(collections.abc.MutableMapping):
    def __init__(self, client: DefaultClient = None, entity: dict = None,
                 content_type: str = '', entity_id: str = "") -> None:
        self._entity = entity
        self._client = client
        self._content_type = content_type
        self._entity_id = entity_id

    @property
    def entity(self) -> dict:
        self._lazy_load()
        return self._entity

    @property
    def client(self) -> DefaultClient:
        return self._client

    def get(self, item):
        return self.entity.get(item)

    def set(self, item: str, value: Any):
        self.entity[item] = value

    def __getitem__(self, item: str):
        return self.entity.get(item)

    def __setitem__(self, key: str, value):
        self.set(key, value)

    def __delitem__(self, key: str):
        del self.entity[key]

    def __len__(self) -> int:
        return len(self.entity)

    def __iter__(self) -> Iterator:
        return iter(self.entity)

    def read(self, **kwargs) -> 'DefaultResource':
        self._entity = None
        self._lazy_load(**kwargs)
        return self

    def _lazy_load(self, **kwargs):
        if not self._entity:
            # lazy load
            self._entity = self._client.fetch(entity_id=self._entity_id, **kwargs)
        return self
