from coopio.IDataService import IDataService
from typing import List, TypeVar, Dict, Generic

T = TypeVar('T')

class IDataProcessor(Generic[T]):
    def __init__(self, primary_data_service: IDataService, peripheral_equity_data_services: List[IDataService] = None):
        self.primary_data_service = primary_data_service
        self.peripheral_data_services = peripheral_equity_data_services if peripheral_equity_data_services else []

    @property
    def data_services(self):
        return [self.primary_data_service] + self.peripheral_data_services

    def retrieve(self, obj_identifier: str, ids: List[str] = None) -> List[T]:
        return self.primary_data_service.retrieve_data(obj_identifier=obj_identifier, ids=ids)

    def add_or_update(self, obj_identifier: str, objs: List[T]) -> List[T]:
        ret = {}
        for service in self.data_services:
            ret[service] = service.add_or_update(obj_identifier=obj_identifier, objs=objs)
        return ret[self.primary_data_service]

    def delete(self, obj_identifier: str, objs: List[T]) -> Dict[IDataService, bool]:
        ret = {}
        for service in self.data_services:
            delete_success = service.delete(obj_identifier=obj_identifier, ids=[str(vars(obj)[obj_identifier]) for obj in objs])
            ret[service] = all(success for equity_id, success in delete_success)

        return ret
