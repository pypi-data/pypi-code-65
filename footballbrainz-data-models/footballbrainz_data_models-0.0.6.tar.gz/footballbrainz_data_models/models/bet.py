from typing import List
from footballbrainz_data_models.models.primary_key import PrimaryKey
from footballbrainz_data_models.models.attribute_definition import AttributeDefinition


class Bet(dict):
    """
    Bet data model for footballbrainz
    """

    def __init__(self, **kwargs):

        if kwargs:
            self.name: str = kwargs.get("name")
            self.display_name: str = kwargs.get("display_name")
            dict.__init__(self, **self.__dict__)
