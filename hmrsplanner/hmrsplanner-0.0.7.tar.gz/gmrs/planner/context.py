from gmrs.graph.node import Node


class Context(Node):
    def addPropertyWithClassAndLabel(self, _class, label, value):
        if self[_class] is None:
            self[_class] = {}

        self[_class][label] = value

    def get(self, _class, label):
        if self[_class] is None:
            return None
        return self[_class][label]
