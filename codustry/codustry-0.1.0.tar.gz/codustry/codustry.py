from codustry.models.craftsman import AllCraftsmanTypes
from typing import Set, Union
from pydantic import BaseModel

class Codustry(BaseModel):
    """This is a graph object."""
    craftmen: Set[AllCraftsmanTypes]
    teams: Set()
    projects: Set()

    money_accounts: dict
