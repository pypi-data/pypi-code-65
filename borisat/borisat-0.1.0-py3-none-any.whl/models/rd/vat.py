from pydantic import BaseModel
from pydantic import Field


class CompanyInfoResponse(BaseModel):
    """use with unnest()"""
    NID: str = Field(alias='n_i_d')

    title_name: str
    name: str
    surname: str

    branch_name:str
    branch_number: int
    branch_title_name:str

    business_first_date: str

    building_name: str
    floor_number: str
    room_number: str

    village_name: str
    house_number:str
    moo_number: str
    soi_name: str
    street_name: str
    thambol: str
    amphur: str
    province: str
    post_code: str
