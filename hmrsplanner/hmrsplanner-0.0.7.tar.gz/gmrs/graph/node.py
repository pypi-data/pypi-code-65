class Node:
    def __init__(self, label=None, type=None, leaf=False):
        self.label = label
        self.type = type or self.__class__.__name__
        self.leaf = leaf
        self.edges = []
        self.typedEdges = {}

    def addEdge(self, edge):
        self.edges.append(edge)

    def addEdges(self, edges):
        for edge in edges:
            self.addEdge(edge)

    def addTypedEdge(self, type, edge):
        self.addEdge(edge)
        self.typedEdges[type] = edge

    def addProperties(self, **properties):
        if not hasattr(self, 'properties'):
            self.properties = {}
        self.properties.update(properties)


class TreeNode(Node):
    def __init__(self):
        super().__init__(self)
        self.parent = None

    def add_parent(self, node, edge_attrs):
        self.parent = Edge(self, node, edge_attrs)


class Edge:
    def __init__(self, nodeA, nodeB, attrs=None):
        self.nodeA = nodeA
        self.nodeB = nodeB
        self.attrs = attrs
