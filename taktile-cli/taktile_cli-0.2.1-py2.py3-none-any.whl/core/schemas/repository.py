from datetime import datetime
from typing import Dict, List, Optional, Union

from beautifultable import BeautifulTable
from pydantic import UUID4, BaseModel

from tktl.core import ExtendedEnum
from tktl.core.utils import flatten


class AccessKind(str, ExtendedEnum):

    # see also corresponding AccessKind on t-api
    OWNER = "owner"
    VIEWER = "viewer"


class Endpoint(BaseModel):
    id: Optional[UUID4] = None
    name: Optional[str] = None
    deployment_id: Optional[UUID4] = None


class RepositoryDeployment(BaseModel):
    id: UUID4
    created_at: datetime
    status: str
    public_docs_url: Optional[str]
    service_type: Optional[str]
    instance_type: Optional[str]
    replicas: Optional[int]
    branch_name: str
    major_version: int
    minor_version: int
    commit_hash: str
    endpoints: List[Endpoint]


class Repository(BaseModel):
    id: UUID4
    ref_id: int
    repository_name: str
    repository_owner: str
    repository_description: Optional[str] = None
    access: AccessKind
    deployments: List[RepositoryDeployment]

    def __str__(self):
        table = BeautifulTable(maxwidth=250)
        rows = self.total_rows()
        table.columns.header = [
            "Branch @ Commit",
            "Deployment Status",
            "REST Docs URL",
            "Version",
            "Created At",
            "Endpoint Name",
            "Endpoint ID",
        ]
        table.rows.header = [f"{self.repository_owner}/{self.repository_name}"] * rows
        table.columns[0] = flatten(
            [
                len(d.endpoints) * [f"{d.branch_name} @ {d.commit_hash}"]
                for d in self.deployments
            ]
        )
        table.columns[1] = flatten(
            [len(d.endpoints) * [f"{d.status}"] for d in self.deployments]
        )
        table.columns[2] = flatten(
            [len(d.endpoints) * [f"{d.public_docs_url}"] for d in self.deployments]
        )
        table.columns[3] = flatten(
            [
                len(d.endpoints) * [f"{d.major_version}.{d.minor_version}"]
                for d in self.deployments
            ]
        )
        table.columns[4] = flatten(
            [len(d.endpoints) * [f"{d.created_at}"] for d in self.deployments]
        )
        table.columns[5] = flatten(
            [[e.name for e in d.endpoints] for d in self.deployments]
        )
        table.columns[6] = flatten(
            [[e.id for e in d.endpoints] for d in self.deployments]
        )
        return table.__str__()

    def total_rows(self):
        return sum([len(d.endpoints) for d in self.deployments])


class ReportResponse(BaseModel):
    deployment_id: UUID4
    endpoint_name: str
    report_type: str
    chart_name: Optional[str] = None
    variable_name: Optional[str] = None
    value: Union[List, Dict]
