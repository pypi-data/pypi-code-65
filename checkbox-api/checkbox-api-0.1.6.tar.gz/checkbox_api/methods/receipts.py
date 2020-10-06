from typing import Any, Dict, Optional

from httpx import Response

from checkbox_api.methods.base import BaseMethod, HTTPMethod, PaginationMixin
from checkbox_api.storage.simple import SessionStorage


class GetReceipts(PaginationMixin, BaseMethod):
    uri = "receipts"


class GetReceipt(BaseMethod):
    def __init__(self, receipt_id: str):
        self.receipt_id = receipt_id

    @property
    def uri(self) -> str:
        return f"receipts/{self.receipt_id}"


class CreateReceipt(BaseMethod):
    method = HTTPMethod.POST
    uri = "receipts/sell"

    def __init__(
        self, receipt: Optional[Dict] = None, **payload,
    ):
        if receipt is not None and payload is not None:
            raise ValueError("'receipt' and '**payload' can not be passed together")
        self.receipt = receipt or payload

    @property
    def payload(self):
        payload = super().payload
        payload.update(self.receipt)
        return payload

    def parse_response(self, storage: SessionStorage, response: Response):
        result = super().parse_response(storage=storage, response=response)
        storage.shift = result["shift"]
        return result


class CreateServiceReceipt(BaseMethod):
    method = HTTPMethod.POST
    uri = "receipts/service"

    def __init__(
        self, payment: Dict[str, Any],
    ):
        self.payment = payment

    @property
    def payload(self):
        payload = super().payload
        payload["payment"] = self.payment
        return payload

    def parse_response(self, storage: SessionStorage, response: Response):
        result = super().parse_response(storage=storage, response=response)
        storage.shift = result["shift"]
        return result


class GetReceiptVisualization(GetReceipt):
    def __init__(self, receipt_id: str, fmt: str = "text", **query):
        super().__init__(receipt_id=receipt_id)
        self.format = fmt
        self.params = query

    @property
    def query(self):
        query = super().query
        query.update(self.params)
        return query

    @property
    def uri(self) -> str:
        uri = super().uri
        return f"{uri}/{self.format}"

    def parse_response(self, storage: SessionStorage, response: Response):
        return response.content


class GetReceiptVisualizationText(GetReceiptVisualization):
    def __init__(self, receipt_id: str, width: int = 50):
        super().__init__(receipt_id=receipt_id, fmt="text", width=width)

    def parse_response(self, storage: SessionStorage, response: Response):
        result = super().parse_response(storage=storage, response=response)
        return result.decode()


class GetReceiptVisualizationHtml(GetReceiptVisualization):
    def __init__(self, receipt_id: str):
        super().__init__(receipt_id=receipt_id, fmt="html")


class GetReceiptVisualizationPdf(GetReceiptVisualization):
    def __init__(self, receipt_id: str):
        super().__init__(receipt_id=receipt_id, fmt="pdf")


class GetReceiptVisualizationQrCode(GetReceiptVisualization):
    def __init__(self, receipt_id: str):
        super().__init__(receipt_id=receipt_id, fmt="qrcode")


class AddExternal(BaseMethod):
    method = HTTPMethod.POST
    uri = "receipts/add-external"

    def __init__(self, data):
        self.data = data

    @property
    def payload(self):
        return self.data
