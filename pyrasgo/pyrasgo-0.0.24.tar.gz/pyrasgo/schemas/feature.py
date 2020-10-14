from typing import Optional
from pydantic import BaseModel


class Feature(BaseModel):
    id: int


class FeatureCreate(BaseModel):
    name: str
    code: Optional[str]
    description: Optional[str]
    columnId: Optional[int]
    featureSetId: Optional[int]
    organizationId: Optional[int]
