class Graph:
    def __init__(self):
        self.src = list()
        self.dest = list()
        self.edges = list()

    def add_edge(self, s, d, e):
        self.src.append(s)
        self.dest.append(d)
        self.edges.append(e)

    @property
    def coo(self):
        """Return COO format graph

        Returns:
            [src, dest], edges
        """
        assert len(self.dest) == len(self.src) == len(self.edges)
        return [self.src, self.dest], self.edges
