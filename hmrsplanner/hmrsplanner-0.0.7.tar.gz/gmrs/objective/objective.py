
from .property_base import Property


class Objective:
    def __init__(self, *properties: [Property]):
        self.properties = properties

