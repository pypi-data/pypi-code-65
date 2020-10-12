from typing import List


class AttributeProjection(dict):
    """
    Class of db projection definition
    """

    def init(self, non_key_attributes=[], projection_type="INCLUDE"):
        if non_key_attributes:
            self.NonKeyAttributes: List = non_key_attributes
        self.ProjectionType: str = projection_type
        dict.__init__(self, **self.__dict__)
