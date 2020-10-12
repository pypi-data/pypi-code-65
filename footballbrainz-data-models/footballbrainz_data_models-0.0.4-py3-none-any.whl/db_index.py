from typing import List
from footballbrainz_data_models.models.primary_key import PrimaryKey
from footballbrainz_data_models.models.attribute_projection import AttributeProjection


class DbIndex(dict):
    """
    Class of db index definition
    """

    def init(self, index_name, key_schema, projection):
        self.IndexName: str = index_name
        self.KeySchema: List[PrimaryKey] = key_schema
        self.Projection: AttributeProjection = projection
        dict.__init__(self, **self.__dict__)
