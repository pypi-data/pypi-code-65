from typing import List

from easyqueue.core.response import ResponseDTO
from easyqueue.core.objects.base.eqobject import EQObject


class BaseCRUDService:

    async def count(self, query: dict) -> ResponseDTO:
        raise NotImplementedError()

    async def create_one(self, element: EQObject) -> ResponseDTO:
        raise NotImplementedError()

    async def create_many(self, elements: List[EQObject]) -> ResponseDTO:
        raise NotImplementedError()

    async def find(self, query: object) -> ResponseDTO:
        raise NotImplementedError()

    async def find_one(self, query: object) -> ResponseDTO:
        raise NotImplementedError()

    async def update_one(self, query: object, update: object) -> ResponseDTO:
        raise NotImplementedError()

    async def update_many(self, query: object, update: object) -> ResponseDTO:
        raise NotImplementedError()

    async def delete_one(self, query: object) -> ResponseDTO:
        raise NotImplementedError()

    async def delete_many(self, query: object) -> ResponseDTO:
        raise NotImplementedError()
