from pydantic import BaseModel, validator


class StringStripModel(BaseModel):
    @validator("*", pre=True)
    def remove_empty_string_and_nones_from_list(cls, v):
        if type(v) != list:
            return v
        return [e for e in v if e is not None and (type(e) == str and e.strip() != "")]

    class Config:
        anystr_strip_whitespace = True


if __name__ == "__main__":

    """Testing"""
    from typing import List
    from pydantic import AnyHttpUrl

    class Images(StringStripModel):
        cloud: List[str]

        class Config:
            allow_mutation = True

    url = "https://basement.cool   "

    images = Images(cloud=[url, "  "])
    print(images)
    print(images.Config.__dict__)
