"""
Ayman Mahmoud - August 2020
Running a search algorithm on the output of the gtfs-graph package

Source 1: https://www.geeksforgeeks.org/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/
Source 2: https://www.bogotobogo.com/python/python_Dijkstras_Shortest_Path_Algorithm.php
Source 3: https://github.com/blkrt/dijkstra-python/blob/3dfeaa789e013567cd1d55c9a4db659309dea7a5/dijkstra.py#L5-L10
Algorithm Implementation using Dijkstra + Networkx Dependent Graph:
https://gist.github.com/aeged/db5bfda411903ecd89a3ba3cb7791a05

Explanation: https://www.youtube.com/watch?v=pVfj6mxhdMw

The algorithm can be automatically implemented with:
https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.dijkstra_path.html

"""
# For graph dependency

import networkx as nx
"First we need to read the graph output"
# path to graph .gpickle must be dynamic
Graph_of_interest = nx.read_gpickle("./output/output_graph_peartree.gpickle")

# dependencies for dijkstra's implementation
from queue import PriorityQueue
from math import inf

"""Dijkstra's shortest path algorithm"""
def dijkstra(graph: 'networkx.classes.graph.Graph', start: str, end: str) -> 'List':
    def backtrace(prev, start, end):
        node = end
        path = []
        while node != start:
            path.append(node)
            node = prev[node]
        path.append(node)
        path.reverse()
        return path

    """get the cost of edges from node -> node
        cost(u,v) = edge_weight(u,v)"""

    def cost(u, v):
        #return graph.get_edge_data(u, v).get('weight')
        graph.get_edge_data(u, v)[0]['length']

    """main algorithm"""
    # predecessor of current node on shortest path
    prev = {}
    # initialize distances from start -> given node i.e. dist[node] = dist(start, node)
    dist = {v: inf for v in list(nx.nodes(graph))}
    # nodes we've visited
    visited = set()
    # prioritize nodes from start -> node with the shortest distance!
    ## elements stored as tuples (distance, node)
    pq = PriorityQueue()

    dist[start] = 0  # dist from start -> start is zero
    pq.put((dist[start], start))

    while 0 != pq.qsize():
        curr_cost, curr = pq.get()
        visited.add(curr)
        print(f'visiting {curr}')
        # look at curr's adjacent nodes
        for neighbor in dict(graph.adjacency()).get(curr):
            # if we found a shorter path
            path = dist[curr] + cost(curr, neighbor)
            if path < dist[neighbor]:
                # update the distance, we found a shorter one!
                dist[neighbor] = path
                # update the previous node to be prev on new shortest path
                prev[neighbor] = curr
                # if we haven't visited the neighbor
                if neighbor not in visited:
                    # insert into priority queue and mark as visited
                    visited.add(neighbor)
                    pq.put((dist[neighbor], neighbor))
                # otherwise update the entry in the priority queue
                else:
                    # remove old
                    _ = pq.get((dist[neighbor], neighbor))
                    # insert new
                    pq.put((dist[neighbor], neighbor))

    print("=== Dijkstra's Algo Output ===")
    print("Distances")
    print(dist)
    print("Visited")
    print(visited)
    print("Previous")
    print(prev)
    # we are done after every possible path has been checked
    return backtrace(prev, start, end), dist[end]

"""

Nodes to test:
'JAJMH_0:SP:10:101', 'JAJMH_0:SP:10:528'
'JAJMH_0:SP:10:503', 'JAJMH_0:SP:10:378'


"""

shortest_path = dijkstra(Graph_of_interest, 'JAJMH_0:SP:10:101', 'JAJMH_0:SP:10:528')