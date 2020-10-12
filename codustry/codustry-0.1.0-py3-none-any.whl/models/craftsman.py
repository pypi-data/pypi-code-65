from datetime import datetime
from typing import Dict, List, Optional, Union

from autoname import AutoName, auto
from pydantic import BaseModel

class AuthorizeLevel(AutoName):
    BDFL = auto()
    CLevel = auto()
    TeamLead = auto()
    Professional = auto()
    Trainee = auto()

class CraftsmanBase(BaseModel):
    codename: str
    inactive: bool = False
    terminated: bool = False
    terminated_reason: Optional[str] = None

    joined: datetime
    contact_channels: Dict
    money_account: Dict
    authorize_level: AuthorizeLevel

    availibility: Dict
    devices: Dict

    karma: List[Dict]
    declaration: List[str]
    skils: List[Dict]



class AnonymousCraftsman(CraftsmanBase):
    proof_of_power: List[Dict]

class Profile(BaseModel):
    first_name: str
    last_name: str

    birthday : datetime

    @classmethod
    def create_from_linkedin(cls, url):
        pass


class Craftsman(CraftsmanBase):
    profile: Profile

AllCraftsmanTypes = Union[Craftsman, AnonymousCraftsman]