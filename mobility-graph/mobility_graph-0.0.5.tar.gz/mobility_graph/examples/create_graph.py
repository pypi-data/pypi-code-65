"""
Ayman Mahmoud - September 2020

An example to run the mobility_graph package
Example 1: Create a generic Graph

"""

from mobility_graph import Graph


g = Graph()

g.add_node(stop_id='a', stop_lon='1', stop_lat='3') # stop_id, stop_name=None, stop_lon='0', stop_lat='0'
g.add_node(stop_id='b', stop_lon='5', stop_lat='2')


g.add_edge('a', 'b', 20, 'walk')


for v in g:
    for w in v.get_connections():
        vid = v.get_id()
        wid = w.get_id()
        print ('( %s , %s, %s, %s)' % (vid, wid, v.get_weight(w), v.get_mode(w)))

for v in g:
    print('g.node_dict[%s]=%s' % (v.get_id(), g.node_dict[v.get_id()]))

