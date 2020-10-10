from pydantic import BaseModel


class _NoSchema(BaseModel):
    class Config:
        extra = "allow"
