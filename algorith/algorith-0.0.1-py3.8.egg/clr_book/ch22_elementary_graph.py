import numpy as np
import networkx as nx
import queue

class Graph():
    def __init__(self,vertices=None):
        ##We'll assume for now a staggered array.
        self.adj=[]
        self.vertices=vertices

    def insert_edge(self,source,dest):
        if len(self.adj)>source:
            self.adj[source].append(dest)
        elif len(self.adj)<source:
            for _ in range(source-len(self.adj)):
                self.adj.append([])
            self.adj[len(self.adj)-1].append(dest)
        else:
            self.adj.append([dest])

def tst():
    g=Graph()
    g.insert_edge(0,1)
    g.insert_edge(0,4)
    g.insert_edge(1,0)
    g.insert_edge(1,4)
    g.insert_edge(1,2)
    g.insert_edge(1,3)
    g.insert_edge(2,1)
    g.insert_edge(2,3)
    g.insert_edge(3,1)
    g.insert_edge(3,4)
    g.insert_edge(3,2)
    g.insert_edge(4,3)
    g.insert_edge(4,0)
    g.insert_edge(4,1)

class ListNode():
    def __init__(self,val,next=None,color="white",\
                pi=None,d=np.inf,key=None):
        self.next=next
        self.val=val
        self.color=color
        self.pi=pi
        self.d=d
        if key is None:
            self.key=val
        else:
            self.key=key


def tst_bfs():
    v=ListNode('v',key=0)
    r=ListNode('r',key=1)
    s=ListNode('s',key=2)
    w=ListNode('w',key=3)
    x=ListNode('x',key=4)
    t=ListNode('t',key=5)
    u=ListNode('u',key=6)
    y=ListNode('y',key=7)
    g=Graph([v,r,s,w,x,t,u,y])

    g.insert_edge(v.key,r)
    g.insert_edge(r.key,v)

    g.insert_edge(r.key,s)
    g.insert_edge(s.key,r)

    g.insert_edge(s.key,w)
    g.insert_edge(w.key,s)

    g.insert_edge(w.key,t)
    g.insert_edge(t.key,w)

    g.insert_edge(w.key,x)
    g.insert_edge(x.key,w)

    g.insert_edge(x.key,u)
    g.insert_edge(u.key,x)

    g.insert_edge(x.key,y)
    g.insert_edge(y.key,x)

    g.insert_edge(u.key,y)
    g.insert_edge(y.key,u)
    bfs(g,v)


def bfs(g,s):
    for i in range(len(g.vertices)):
        if i!=s.key:
            u=g.vertices[i]
            u.color="white"
            u.d=np.inf
            u.pi=None
    s.color="grey"
    s.d=0
    s.pi=None
    q=queue.Queue()
    q.put(s)
    while q.qsize()>0:
        u=q.get()
        for v in g.adj[u.key]:
            if v.color=="white":
                v.color="grey"
                v.d=u.d+1
                v.pi=u
                q.put(v)
        u.color="black"


