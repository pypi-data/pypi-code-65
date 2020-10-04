"""
Utility functions for common graph related operations
"""
import mobility_graph.graphs
from heapq import heappush, heappop
from itertools import count

def save_graph(G):
    # Save graph to memory if nx is used
    #nx.write_gpickle(G, "./output_graph.gpickle")
    pass
    # TODO: Still need to find a way to save the graph class, maybe look into saving objects in a file

def draw_graph(G):
    pass
    # TODO: Still need to find a way to represent the graph class graphically

##########################################
# helpers for betweenness centrality
##########################################


def _single_source_dijkstra_path_basic(G, s, weight):
    # modified from Eppstein
    S = []
    P = {}
    for v in G:
        P[v.get_id()] = []
    sigma = dict.fromkeys(G.get_nodes(), 0.0)  # sigma[v]=0 for v in G
    D = {}
    sigma[s] = 1.0
    push = heappush
    pop = heappop
    seen = {s: 0}
    c = count()
    Q = []  # use Q as heap with (distance,node id) tuples
    push(Q, (0, next(c), s, s))
    while Q:
        (dist, _, pred, v) = pop(Q)
        if v in D:
            continue  # already searched this node.
        sigma[v] += sigma[pred]  # count paths
        S.append(v)
        D[v] = dist
        for w in G.get_node(v).get_connections():
            vw_dist = dist + G.get_node(v).get_weight(w)
            if w not in D and (w not in seen or vw_dist < seen[w]):
                seen[w.id] = vw_dist
                push(Q, (vw_dist, next(c), v, w.id))
                sigma[w.id] = 0.0
                P[w.id] = [v]
            elif vw_dist == seen[w.id]:  # handle equal paths
                sigma[w.id] += sigma[v]
                P[w.id].append(v)
    return S, P, sigma


def _accumulate_basic(betweenness, S, P, sigma, s):
    delta = dict.fromkeys(S, 0)
    while S:
        w = S.pop()
        if sigma[w]:
            coeff = (1 + delta[w]) / sigma[w]
        else:
            coeff = 0
        for v in P[w]:
            delta[v] += sigma[v] * coeff
        if w != s:
            betweenness[w] += delta[w]
    return betweenness


def _accumulate_endpoints(betweenness, S, P, sigma, s):
    betweenness[s] += len(S) - 1
    delta = dict.fromkeys(S, 0)
    while S:
        w = S.pop()
        if sigma[w]:
            coeff = (1 + delta[w]) / sigma[w]
        else:
            coeff = 0
        for v in P[w]:
            delta[v] += sigma[v] * coeff
        if w != s:
            betweenness[w] += delta[w] + 1
    return betweenness


def _accumulate_edges(betweenness, S, P, sigma, s):
    delta = dict.fromkeys(S, 0)
    while S:
        w = S.pop()
        if sigma[w]:
            coeff = (1 + delta[w]) / sigma[w]
        else:
            coeff = 0
        for v in P[w]:
            c = sigma[v] * coeff
            if (v, w) not in betweenness:
                betweenness[(w, v)] += c
            else:
                betweenness[(v, w)] += c
            delta[v] += c
        if w != s:
            betweenness[w] += delta[w]
    return betweenness


def _rescale(betweenness, n, normalized, directed=False, k=None, endpoints=False):
    if normalized:
        if endpoints:
            if n < 2:
                scale = None  # no normalization
            else:
                # Scale factor should include endpoint nodes
                scale = 1 / (n * (n - 1))
        elif n <= 2:
            scale = None  # no normalization b=0 for all nodes
        else:
            scale = 1 / ((n - 1) * (n - 2))
    else:  # rescale by 2 for undirected graphs
        if not directed:
            scale = 0.5
        else:
            scale = None
    if scale is not None:
        if k is not None:
            scale = scale * n / k
        for v in betweenness:
            betweenness[v] *= scale
    return betweenness


def _rescale_e(betweenness, n, normalized, directed=False, k=None):
    if normalized:
        if n <= 1:
            scale = None  # no normalization b=0 for all nodes
        else:
            scale = 1 / (n * (n - 1))
    else:  # rescale by 2 for undirected graphs
        if not directed:
            scale = 0.5
        else:
            scale = None
    if scale is not None:
        if k is not None:
            scale = scale * n / k
        for v in betweenness:
            betweenness[v] *= scale
    return betweenness