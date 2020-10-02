from gmrs.graph.node import Node


class Operator(Node):
    def __init__(self, type):
        super().__init__(self)
        self.type = type
        pass
