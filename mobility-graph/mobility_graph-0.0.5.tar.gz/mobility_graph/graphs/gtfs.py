from .graph import Graph, Node

class GTFS(Graph):
    """
        This class adapts GTFS features with Graph
        use package mobility-graph
    """
    # you can assign variable attributes

    def __init__(self, type='GTFS'):
        # Initialize a graph of n vertices
        # self.nodes = 0
        # Graph.__init__(self) # both are correct
        super().__init__()
        self.node_dict = {}
        self.num_nodes = 0

    def __iter__(self):
        return iter(self.node_dict.values())

    def add_node(self, stop_id, stop_name=None, stop_lon='0', stop_lat='0'):
        self.num_nodes = self.num_nodes + 1
        new_node = Node(stop_id, stop_name, stop_lon, stop_lat)
        self.node_dict[stop_id] = new_node
        return new_node

    def get_node(self, n):
        if n in self.node_dict:
            return self.node_dict[n]
        else:
            return None
    @classmethod
    def print_info(cls):
        print("This class does...")
    @staticmethod
    # it is a method that doesn't change anything
    def add(n):
        return n

    def add_edge(self, from_id, to_id, cost=0, mode='GTFS', key=None):
        # create edge between two vertices/nodes
        # remember that here you don't have get parent id anymore
        #
        add_edge = True
        if key is None:
            key = ''
        if add_edge:
            self.node_dict[from_id].add_neighbor(
                self.node_dict[to_id], weight=cost, mode=mode, key=key)
            self.node_dict[to_id].add_neighbor(
                self.node_dict[from_id], weight=cost, mode=mode, key=key)

    def del_Edge(self, n1, n2):
        # deletes edge between two vertices/nodes
        pass

    def get_nodes(self):
        return self.node_dict.keys()

    def isEdge(self, n1, n2):
        # Determine if an edge is in the graph
        return None

    def build_graph(self):
        pass

    def visualize(self, mode='plain'):
        """
        Inspired from: https://towardsdatascience.com/easy-steps-to-plot-geographic-data-on-a-map-python-11217859a2db
        """
        if mode == 'plain':
            print("Printing nodes in plain mode")
            # get_map(a, 1)
        elif mode == 'sat':
            print("Getting satellite data")
            # get_map(a, 2)
        elif mode == 'map':
            print("Getting map data")
            # get_map(a, 3)
        else:
            print("An error occured. please check mode")
