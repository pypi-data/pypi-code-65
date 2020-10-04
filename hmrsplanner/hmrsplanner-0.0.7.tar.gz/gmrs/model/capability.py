from gmrs.graph.node import Node


class Capability(Node):
    def __init__(self, id, **properties):
        super().__init__(id, leaf=True)
