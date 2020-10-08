from lfr.netlistgenerator.v2.constructionnode import ConstructionNode
from networkx import nx


class ConstructionGraph(nx.DiGraph):

    def __init__(self) -> None:
        self.construction_nodes = dict()

    def add_construction_node(self, node: ConstructionNode) -> None:
        self.add_construction_node[node.id] = node
        self.add_node(node.id)
