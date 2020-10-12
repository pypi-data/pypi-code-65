import numpy as np

class Node():
    def __init__(self, val):
        self.val = val

class Graph():
    def __init__(self, edges):
        self.edges = edges

## https://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/

graph = {'A': set(['B', 'C']),
         'B': set(['A', 'D', 'E']),
         'C': set(['A', 'F']),
         'D': set(['B']),
         'E': set(['B', 'F']),
         'F': set(['C', 'E'])}

def dfs(graph, start):
    visited, stack = set(), [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            stack.extend(graph[vertex] - visited)
    return visited

dfs(graph, 'A') # {'E', 'D', 'F', 'A', 'C', 'B'}

## Recursive version of depth first search.
def dfs_r(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for next in graph[start] - visited:
        dfs_r(graph, next, visited)
    return visited


#a=np.random.choice(2,size=(10,10))
def count_clouds(a):
    visited = set(); clouds = 0
    for i in range(len(a)):
        for j in range(len(a[0])):
            if a[i,j]==0 and (i,j) not in visited:
                clouds+=1
                ##Now do depth first search.
                stack = [(i,j)]
                while stack:
                    curr = stack.pop()
                    if curr not in visited:
                        visited.add(curr)
                        (ix,jx) = curr
                        if ix < len(a)-1 and a[ix+1,jx]==0:
                            stack.append((ix+1,jx))
                        if jx < len(a[0])-1 and a[ix,jx+1]==0:
                            stack.append((ix,jx+1))
    return clouds


def tst_count_clouds():
    a = np.ones((10,10))
    a[:2,:2]=0; a[2,2]=0
    
    a = np.ones((10,10))
    a[1:5,3:4]=0; a[8,8]=0
    a[9,9]=0
    
    a=np.random.choice(2,size=(10,10))
    clouds = count_clouds(a)


