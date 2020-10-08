from blobhub.blob import Revision


class Vertex:

    def __init__(self):
        pass


class Vertices:

    def __init__(self, graph: Graph):
        self.graph = graph

    def find(self, id: str):
        pass


class Graph:

    def __init__(self, revision: Revision):
        self.revision = revision
        self.vertices = Vertices(graph=self)
