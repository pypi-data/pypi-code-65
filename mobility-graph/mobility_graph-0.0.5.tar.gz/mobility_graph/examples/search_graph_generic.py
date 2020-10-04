"""
Ayman Mahmoud - September 2020
an example to run a search on the following basic graph:

#########################################
#   (a)------------------------(b)      #
#    *                 ------ *-        #
#     *           -----      *-         #
#      *       ---          *-          #
#       *   ---            *-           #
#        *-               *-            #
#       (c)             (d)             #
#                                       #
#   [-- Metro, ** Walk]                 #
#                                       #
#########################################
"""

from mobility_graph import Graph

g = Graph()

g.add_node(stop_id='a', stop_lon='1', stop_lat='3') # stop_id, stop_name=None, stop_lon='0', stop_lat='0'
g.add_node(stop_id='b', stop_lon='5', stop_lat='2')
g.add_node(stop_id='c', stop_lon='2', stop_lat='-2')
g.add_node(stop_id='d', stop_lon='7', stop_lat='4')
g.add_node(stop_id='e', stop_lon='7', stop_lat='4')
g.add_node(stop_id='f', stop_lon='7', stop_lat='4') # this is a node that has zero connections with other stops

g.add_edge('a', 'c', 20, 'walk')
g.add_edge('a', 'b', 7, 'metro')
g.add_edge('c', 'b', 7, 'metro')
g.add_edge('d', 'b', 10, 'metro')
g.add_edge('d', 'b', 10, 'walk')
g.add_edge('d', 'e', 17, 'walk')

"""
g.search_bfs('a','e') # expected output: Shortest Path =  a b d e
g.search_bfs('c','e') # expected output: Shortest Path =  c b d e
g.search_bfs('c','c') # expected output: You are at the destination
g.search_bfs('c','f') # expected output: A connecting path doesn't exist :(
g.search_bfs('b','a') # expected output: Shortest Path =  b a
"""

#betweenness = g.betweenness_centrality(k=None, normalized=True,weight='a',endpoints=False,seed=None)

#g.search_optimization_gurobi('a','e')

g.search_dijkstra('a', 'c')
g.search_dijkstra('a', 'e')
g.search_dijkstra('a')