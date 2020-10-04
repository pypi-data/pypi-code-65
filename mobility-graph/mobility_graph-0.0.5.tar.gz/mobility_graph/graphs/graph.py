"""
Ayman Mahmoud - August 2020

"""
from ..utils import common, graph_utils

class Graph(object):
    """
    This class outlines the structure of a graph, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    Class inspiration: https://gist.github.com/eovares/4035265, https://github.com/bmander/graphserver/blob/master/core/graph.h

    Abstraction graph example: https://www.geeksforgeeks.org/abstract-classes-in-python/
    Graph theory in python: https://www.python-course.eu/graphs_python.php

    Class implementation: https://www.bogotobogo.com/python/python_graph_data_structures.php

    """
    def __init__(self):
        # Initialize a graph of n vertices
        # self.nodes = 0
        self.node_dict = {}
        self.num_nodes = 0
        self.nx = common.nx.MultiDiGraph()  # for comparison between speed in search
        self.edge_count = 0

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

    def add_edge(self, frm, to, weight=0, mode='NA', color=None):
        # create edge between two vertices/nodes
        # TODO: add a flag to differentiate between adding a one way edge or both way edges
        add_edge = True
        if frm not in self.node_dict:
            self.add_node(frm, 'NA', 'NA')
            print('The node', frm, 'does not exist, please add missing information in order to add the node to the database.')
            add_edge = False
        if to not in self.node_dict:
            self.add_node(to, 'NA', 'NA')
            print('The node', to,'does not exist, please add missing information in order to add the node to the database.')
            add_edge = False
        if color == None:
            color = ''
            r, g, b = (0, 0, 0)
        else:
            r = int(color[:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:], 16)

        if add_edge:
            self.node_dict[frm].add_neighbor(self.node_dict[to], weight, mode, 'r')
            self.node_dict[to].add_neighbor(self.node_dict[frm], weight, mode, 'r')
            self.edge_count += 1

    def del_Edge(self, n1, n2):
        # deletes edge between two vertices/nodes
        pass

    def get_edge_count(self):
        return self.edge_count

    def get_nodes(self):
        return self.node_dict.keys()

    def isEdge(self, n1, n2):
        # Determine if an edge is in the graph
        pass

    def visualize(self):
        # visualize Graph based lon and lat
        pass

        # TODO: move utility functions in utils if possible
    def printSolution(self, dist, source, destination = None, path=None):
        if destination is None:
            print("Vertex \tDistance from Source node: ",'(' + source + ')' + '\tPath')
            for node in self.get_nodes():
                print(node, "\t", dist[node], "\t", path[node])
        else:
            print("Distance from Source node: ", '(' + source + ') ' +
                  'to destination node' + '(' + destination + '): ' + str(dist[destination]))
            print("Shortest Path = ", *path[destination])


    # minimum distance value, from the set of vertices
    # not yet included in shortest path tree
    def minDistance(self, dist, sptSet):
        # Initilalize minimum distance for next node
        min = float('inf')
        min_index = None
        # Search not nearest vertex not in the
        # shortest path tree
        for v in self.get_nodes():
            if dist[v] < min and sptSet[v] == False:
                min = dist[v]
                min_index = v

        return min_index

    def search_dijkstra(self, origin, destination=None):
        """
        Dijkstra’s algorithm is a Greedy algorithm and time complexity is O(VLogV) (with the use of Fibonacci heap).
        Intro: https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/
        - We maintain two sets, one set contains vertices included in shortest path tree,
        other set includes vertices not yet included in shortest path tree.
        :param origin:
        :param destination:
        :return:
        """
        dist = {x: float('inf') for x in self.get_nodes()}
        # visited = {x: {False} for x in self.get_nodes()}
        dist[origin] = 0
        sptSet = {x: False for x in self.get_nodes()}
        # path = {x: set(origin) for x in self.get_nodes()}
        path = {x: list(origin) for x in self.get_nodes()}

        for cout in self.get_nodes():
            # Pick the minimum distance vertex from
            # the set of vertices not yet processed.
            # u is always equal to src in first iteration
            u = self.minDistance(dist, sptSet)
            if u is None:
                break
            # Put the minimum distance vertex in the
            # shotest path tree
            sptSet[u] = True

            # Update dist value of the adjacent vertices
            # of the picked vertex only if the current
            # distance is greater than new distance and
            # the vertex in not in the shortest path tree
            for w in self.get_node(u).get_connections():
                if self.get_node(u).get_weight(w) > 0 and sptSet[w.id] == False and \
                        dist[w.id] > dist[u] + self.get_node(u).get_weight(w):
                    dist[w.id] = dist[u] + self.get_node(u).get_weight(w)
                    if u is not origin:
                        #path[w.id].add(u)
                        temp_path = path[u]
                        if u not in temp_path:
                            temp_path.append(u)
                        for x in temp_path:
                            if x not in path[w.id]:
                                path[w.id].append(x) # update in set will not work because it sorts elements

        for node in path:
            if dist[node] == float('inf'):
                path[node] = []
            else:
                if node not in path[node]:
                    path[node].append(node)

        if destination is None:
            self.printSolution(dist, source= origin, path=path)
        else:
            self.printSolution(dist, origin, destination, path)



    def search_bellman_ford(self, origin, destination):
            """
            Dijkstra doesn’t work for Graphs with negative weight edges, Bellman-Ford works for such graphs.
            Bellman-Ford is also simpler than Dijkstra and suites well for distributed systems.
            But time complexity of Bellman-Ford is O(VE), which is more than Dijkstra.
            Intro: https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/
            :param origin:
            :param destination:
            :return:
            """
            pass


    def search_dfs_visited(self, n, n2, visited):

        # Mark the current node as visited
        # you can also use the stack utility for the visited. Check P2-1 Search.py
        visited[n] = {True}
        print(n)

        # Recur for all the vertices
        # adjacent to this vertex
        for i in self.get_node(n).get_connections():
            if visited[i.id] == {False}:
                if visited[n2] == {False}:
                    self.search_dfs_visited(i.id, n2, visited)

    def search_dfs(self, n, n2):
        """
        intro: https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/
        go in depth when possible and when reach a dead end we retreat
        :param n: start node
        :param n2: destination node
        :return: an set of all possible paths between the two nodes
        """
        # Mark all the vertices as not visited
        visited = {x: {False} for x in self.get_nodes()}
        if n == n2:
            print("You are at the destination")
            return None
        # Call the recursive helper function to print
        # DFS traversal starting from all vertices one
        # by one
        else:
            for i in self.get_nodes():
                if visited[i] == {False}:
                    if visited[n2] == {False}:
                        self.search_dfs_visited(i, n2, visited)
        if visited[n2] == {True}:
            print("you arrived to the destination")
            # TODO: add metrics

    def search_bfs(self, start, goal):
        """
        Intro: https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/
        path =
        :param n: start node
        :param n2: destination node
        :return: an set of all possible paths between the two nodes, for now it just prints the nodes visited
        """

        # Verify we're not at the destination
        if start == goal:
            print("You are at the destination")
            return None

        # Mark all the vertices as not visited
        visited = {x: {False} for x in self.get_nodes()} # also explored
        # Create a queue for BFS
        Queue = common.Queue()
        # Mark the source node as
        # visited and enqueue it
        Queue.push((start))
        # visited[start] = True

        while not Queue.isEmpty(): # also while Queue...

            # Dequeue a vertex from
            # queue and print it
            path = Queue.pop()
            node = path[-1] # as an example if in the queue you have ['a','c','d'] then the node will be 'd'
            # print(node, end=" ")

            # Get all adjacent vertices of the
            # dequeued vertex s. If a adjacent
            # has not been visited, then mark it
            # visited and enqueue it
            if visited[node] == {False}:
                for i in self.get_node(node).get_connections():
                    new_path = list(path)
                    new_path.append(i.id)
                    Queue.push((new_path))

                    #if visited[goal] == {True}:
                    if i.id == goal:
                        print("You arrived to the destination")
                        print("Shortest Path = ", *new_path)
                        return
                visited[node] = {True}

        print("A connecting path doesn't exist :(")
        return

    def search_optimization_gurobi(self, start, goal):
        """
        based on: https://www.gurobi.com/documentation/9.0/quickstart_mac/py_netflow_py_example.html
        to learn more about network analysis: https://towardsdatascience.com/i-built-the-t-with-python-and-revamped-it-632127364f4e
        :return:
        """
        import gurobipy as gp
        from gurobipy import GRB
        # 1. Build a cost matrix for all edges (#TODO: move this part to the graph structure) # example g.model
        # go through all edges and get the weight
        model = gp.Model('search_path')
        "1. add model variables"
        # get number of nodes in graph
        # n_nodes = len(self.get_nodes()) # you can also transform it later to self.get_node_count()
        # n_edges = self.get_edge_count()

        # Initialize decision variables for ground set:
        # x[i,j] == 1 if the trip i to j is going to take place.
        # x = model.addMVar(shape=(n_nodes, n_nodes), vtype=GRB.BINARY, name='x')

        # e[i,j] == weight if the edge i to j exists, if it doesn't exists the weight is set to inf.
        # e = model.addMVar(shape=(n_nodes, n_nodes), vtype=GRB.INTEGER, name='e')

        # v[i] is the variable for the visited node
        # v = model.addMVar(shape=(n_nodes), vtype=GRB.BINARY, name='v')

        edges = gp.tuplelist()
        cost = {}

        for v in self:
            for w in v.get_connections():
                if (v.id, w.id) not in edges:
                    edges.append((v.id, w.id))
                    cost[v.id, w.id] = v.get_weight(w)
                if (w.id, v.id) not in edges:
                    edges.append((w.id, v.id))
                    cost[w.id, v.id] = v.get_weight(w)

        x = model.addVars(edges, obj=cost, name="x")

        for i in self.get_nodes():
            model.addConstr(sum(x[i, j] for i, j in edges.select(i, '*')) - sum(x[j, i] for j, i in edges.select('*', i)) ==
                        (1 if i == start else -1 if i == goal else 0), 'node%s_' % i)

        model.optimize()

        if model.status == GRB.Status.OPTIMAL:
            print('The final solution is:')
            for i, j in edges:
                if (x[i, j].x > 0):
                    print(i, j, x[i, j].x)

    def betweenness_centrality(self, k=None, normalized=True, weight=None,
                           endpoints=False, seed=None):
        """
        intro: https://www.geeksforgeeks.org/betweenness-centrality-centrality-measure/
        Algorithm: https://networkx.github.io/documentation/stable/_modules/networkx/algorithms/centrality/betweenness.html
        In graph theory, betweenness centrality is a measure of centrality in a graph based on shortest paths.
        For every pair of vertices in a connected graph, there exists at least one shortest path between the vertices
        such that either the number of edges that the path passes through (for unweighted graphs) or the sum of the
        weights of the edges (for weighted graphs) is minimized. The betweenness centrality for each vertex is the
        number of these shortest paths that pass through the vertex.

        Betweenness centrality finds wide application in network theory: it represents the degree of which nodes
        stand between each other. For example, in a telecommunications network, a node with higher betweenness
        centrality would have more control over the network, because more information will pass through that node.
        Betweenness centrality was devised as a general measure of centrality: it applies to a wide range
        of problems in network theory, including problems related to social networks, biology, transport
        and scientific cooperation.

        Betweenness centrality of a node the node is the sum of the  fraction of all-pairs
        shortest paths that pass through the node

        .. math::

           c_B(v) =\sum_{s,t \in V} \frac{\sigma(s, t|v)}{\sigma(s, t)}

        where $V$ is the set of nodes, $\sigma(s, t)$ is the number of
        shortest $(s, t)$-paths,  and $\sigma(s, t|v)$ is the number of
        those paths  passing through some  node $v$ other than $s, t$.
        If $s = t$, $\sigma(s, t) = 1$, and if $v \in {s, t}$,
        $\sigma(s, t|v) = 0$ [2]_.


        :param k: int, optional (default=None)
          If k is not None use k node samples to estimate betweenness.
          The value of k <= n where n is the number of nodes in the graph.
          Higher values give better approximation.
        :param normalized: bool, optional
          If True the betweenness values are normalized by `2/((n-1)(n-2))`
          for graphs, and `1/((n-1)(n-2))` for directed graphs where `n`
          is the number of nodes in G.
        :param weight:None or string, optional (default=None)
          If None, all edge weights are considered equal.
          Otherwise holds the name of the edge attribute used as weight.
        :param endpoints:bool, optional
          If True include the endpoints in the shortest path counts.
        :param seed:  integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
        Note that this is only used if k is not None.
        :return:
        nodes : dictionary
        Dictionary of nodes with betweenness centrality as the value.
        """
        betweenness = dict.fromkeys(self.get_nodes(), 0.0)  # b[v]=0 for v in G
        if k is None:
            nodes = self.get_nodes()
        else:
            common.random.seed(seed)
            nodes = common.random.sample(self.get_nodes(), k)
        for s in nodes:
            # single source shortest paths
            S, P, sigma = graph_utils._single_source_dijkstra_path_basic(self, s, weight)
                # accumulation
            if endpoints:
                betweenness = graph_utils._accumulate_endpoints(betweenness, S, P, sigma, s)
            else:
                betweenness = graph_utils._accumulate_basic(betweenness, S, P, sigma, s)

                # rescaling
        betweenness = graph_utils._rescale(betweenness, len(self.get_nodes()), normalized=normalized,
                               directed=True, k=k) # because it is directed
        return betweenness


class Node:
    """
    Attributes:
    "stop_id", "stop_code", "stop_name", "stop_desc", "platform_code",
    "platform_name", "stop_lat", "stop_lon", "stop_address", "zone_id",
    "stop_url", "level_id", "location_type", "parent_station", "wheelchair_boarding"

    This class is used to organize all Stops so that they can easily be used to form the network nodes
    """
    def __init__(self, id, name, lon, lat):
        self.id = id
        self.name = name
        self.lon = lon
        self.lat = lat
        self.tags = {}
        self.adjacent = {}
        self.mode = {}
        self.color = {}
        self.key = {}

    def add_neighbor(self, neighbor, weight=0, mode='NA', color=None, key=None):
        self.adjacent[neighbor] = weight
        self.mode[neighbor] = mode
        self.color[neighbor] = color
        self.key[neighbor] = key

    def del_neighbor(self, neighbor):
        self.__delattr__(neighbor)

    def get_connections(self):
        return self.adjacent.keys()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

    def get_mode(self, neighbor):
        return self.mode[neighbor]

    def get_color(self, neighbor):
            return self.color[neighbor]

    def __str__(self):
        string = 'Name: ' + self.id + '\nCoordinates: ' + '(' + str(self.lat) \
                 + ', ' + str(self.lon) + ')' + ' \nAdjacent: ' + str([x.id for x in self.adjacent])
        return string
