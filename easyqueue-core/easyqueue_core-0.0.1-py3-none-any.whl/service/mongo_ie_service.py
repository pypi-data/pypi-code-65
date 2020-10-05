from typing import Dict, List, Type

from easyqueue.core.response import ResponseDTO
from easyqueue.utils.validation import TypeValidator
from easyqueue.core.objects.base.eqobject import EQObject
from easyqueue.service.base_ie_service import BaseIEService
from easyqueue.database.mongo.repository import MongoRepository


class MongoIEService(BaseIEService):

    repository: MongoRepository = None
    base_object_class: Type = EQObject

    def __init__(self, repository: MongoRepository = None, base_object_class: Type = None) -> None:
        self.repository = repository if repository is not None else self.repository
        self.base_object_class = base_object_class if base_object_class is not None else self.base_object_class

    async def count(self, query: Dict) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        return await self.repository.count(query=query)

    async def import_one(self, element: Dict) -> ResponseDTO:
        return await self.repository.create_one(element=element, validate=True)

    async def import_many(self, elements: List[Dict]) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='elements', element=elements, type_class=list, allow_none=False)
        return await self.repository.create_many(elements=elements, validate=True)

    async def export_one(self, query: Dict) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        return await self.repository.find_one(query=query)

    async def export_many(self) -> ResponseDTO:
        return await self.repository.find(query={})
