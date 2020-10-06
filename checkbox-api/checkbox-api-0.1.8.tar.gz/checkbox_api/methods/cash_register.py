from httpx import Response

from checkbox_api.methods.base import BaseMethod, PaginationMixin
from checkbox_api.storage.simple import SessionStorage


class GetCashRegisters(PaginationMixin, BaseMethod):
    uri = "cash-registers"


class GetCashRegister(BaseMethod):
    def __init__(self, cash_register_id: str):
        self.cash_register_id = cash_register_id

    @property
    def uri(self) -> str:
        return f"cash-registers/{self.cash_register_id}"


class GetCashRegisterInfo(BaseMethod):
    uri: str = "cash-registers/info"

    def parse_response(self, storage: SessionStorage, response: Response):
        result = super().parse_response(storage=storage, response=response)
        storage.cash_register = result
        return result
