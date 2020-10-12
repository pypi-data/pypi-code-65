from typing import Set, Union
from codustry.models.craftsman import AllCraftsmanTypes
from pydantic import BaseModel

class Team(BaseModel):
    leader: AllCraftsmanTypes

    members: Set[AllCraftsmanTypes]
