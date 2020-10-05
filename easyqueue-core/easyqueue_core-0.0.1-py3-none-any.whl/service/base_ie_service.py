from typing import List

from easyqueue.core.response import ResponseDTO
from easyqueue.core.objects.base.eqobject import EQObject


class BaseIEService:

    async def count(self, query: object) -> ResponseDTO:
        raise NotImplementedError()

    async def import_one(self, element: EQObject) -> ResponseDTO:
        raise NotImplementedError()

    async def import_many(self, elements: List[EQObject]) -> ResponseDTO:
        raise NotImplementedError()

    async def export_one(self, query: object) -> ResponseDTO:
        raise NotImplementedError()

    async def export_many(self) -> ResponseDTO:
        raise NotImplementedError()
