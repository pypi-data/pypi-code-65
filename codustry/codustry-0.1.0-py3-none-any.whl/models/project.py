from typing import Optional
from pydantic.main import BaseModel


class Project(BaseModel):
    clients: Optional[dict]