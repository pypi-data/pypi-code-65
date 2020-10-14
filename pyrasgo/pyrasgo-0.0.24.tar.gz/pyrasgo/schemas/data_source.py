from pydantic import BaseModel

from pyrasgo.schemas.organization import Organization


class DataSource(BaseModel):
    id: int


class DataSourceCreate(BaseModel):
    name: str
    abbreviation: str
    organization: Organization
