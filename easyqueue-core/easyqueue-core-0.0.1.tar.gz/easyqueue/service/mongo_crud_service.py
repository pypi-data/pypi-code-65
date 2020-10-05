from typing import Dict, List, Type

from easyqueue.core.response import ResponseDTO
from easyqueue.utils.validation import TypeValidator
from easyqueue.core.objects.base.eqobject import EQObject
from easyqueue.service.base_crud_service import BaseCRUDService
from easyqueue.database.mongo.repository import MongoRepository


class MongoCRUDService(BaseCRUDService):

    repository: MongoRepository = None
    base_object_class: Type = EQObject

    def __init__(self, repository: MongoRepository = None, base_object_class: Type = None) -> None:
        self.repository = repository if repository is not None else self.repository
        self.base_object_class = base_object_class if base_object_class is not None else self.base_object_class

    @classmethod
    def __get_validated_element(cls, element: EQObject, allow_none: bool = False) -> Dict:
        validated_object = None
        if isinstance(element, cls.base_object_class):
            validated_object = element.json()
        else:
            TypeValidator.raise_validation_element_type(
                element_name='element', element=element, type_class=EQObject, allow_none=allow_none)

        return validated_object

    async def count(self, query: Dict) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        return await self.repository.count(query=query)

    async def create_one(self, element: EQObject) -> ResponseDTO:
        return await self.repository.create_one(element=self.__get_validated_element(element))

    async def create_many(self, elements: List[EQObject]) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='elements', element=elements, type_class=list, allow_none=False)
        validated_elements = []
        for element in elements:
            validated_elements.append(self.__get_validated_element(element))
        return await self.repository.create_many(elements=validated_elements)

    async def find(self, query: Dict, skip: int = 0, limit: int = 0) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        response_result = await self.repository.find(query=query, skip=skip, limit=limit)
        raw_results = response_result.data
        parsed_results = []
        for raw_result in raw_results:
            parsed_results.append(self.base_object_class.from_json(raw_result))
        response_result_parsed = ResponseDTO(code=response_result.code, data=parsed_results)
        return response_result_parsed

    async def find_one(self, query: Dict) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        response_result  = await self.repository.find_one(query=query)
        data_result = self.base_object_class.from_json(response_result.data)
        response_result_parsed = ResponseDTO(code=response_result.code, data=data_result)
        return response_result_parsed

    async def update_one(self, query: Dict, update: Dict) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        TypeValidator.raise_validation_element_type(
            element_name='update', element=update, type_class=dict, allow_none=False)
        return await self.repository.update_one(query=query, update=update)

    async def update_many(self, query: Dict, update: Dict) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        TypeValidator.raise_validation_element_type(
            element_name='update', element=update, type_class=dict, allow_none=False)
        return await self.repository.update_many(query=query, update=update)

    async def delete_one(self, query: Dict) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        return await self.repository.delete_one(query=query)

    async def delete_many(self, query: Dict) -> ResponseDTO:
        TypeValidator.raise_validation_element_type(
            element_name='query', element=query, type_class=dict, allow_none=False)
        return await self.repository.delete_many(query=query)
