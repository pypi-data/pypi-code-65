from httpx import Response

from checkbox_api.methods.base import BaseMethod, HTTPMethod, PaginationMixin
from checkbox_api.storage.simple import SessionStorage


class GetReports(PaginationMixin, BaseMethod):
    uri = "reports"


class GetReport(BaseMethod):
    def __init__(self, report_id: str):
        self.report_id = report_id

    @property
    def uri(self) -> str:
        return f"reports/{self.report_id}"


class CreateReport(BaseMethod):
    method = HTTPMethod.POST
    uri = "reports"


class GetReportVisualization(GetReport):
    def __init__(self, report_id: str, fmt: str = "text", **query):
        super().__init__(report_id=report_id)
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


class GetReportVisualizationText(GetReportVisualization):
    def __init__(self, report_id: str, width: int = 50):
        super().__init__(report_id=report_id, fmt="text", width=width)

    def parse_response(self, storage: SessionStorage, response: Response):
        result = super().parse_response(storage=storage, response=response)
        return result.decode()
