from typing import Optional
from pydantic import BaseModel

from pyrasgo.schemas.data_source import DataSource


class FeatureSet(BaseModel):
    id: int


class FeatureSetCreate(BaseModel):
    snowflakeTable: str
    name: str
    dataSource: DataSource
    granularity: Optional[str]
