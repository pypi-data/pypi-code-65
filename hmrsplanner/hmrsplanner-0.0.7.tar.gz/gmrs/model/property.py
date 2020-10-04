from gmrs.graph.node import Node


class Property(Node):
    def __init__(self, type, value, unit):
        self.type = type
        self.value = value
        self.unit = unit
