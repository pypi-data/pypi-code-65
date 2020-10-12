import numpy as np
from importlib import reload


def mat_chain_order(p):
    n=len(p)-1
    m=np.zeros((n,n))
    s=np.zeros((n,n))
    for l in range(1,n):
        for i in range(n-l):
            j=i+l
            m[i,j]=np.inf
            for k in range(i,j):
                cost=m[i,k]+m[k+1,j]+p[i]*p[k+1]*p[j+1]
                if cost<m[i,j]:
                    m[i,j]=cost
                    s[i,j]=k
    return m,s

def print_opt_parenth(s,i,j):
    if j==i:
        print("A"+str(i+1),end="")
    else: 
        print("(",end="")
        print_opt_parenth(s,i,int(s[i,j]))
        print_opt_parenth(s,int(s[i,j])+1,j)
        print(")",end="")

def mult_matrices(l_m):
    p=[]
    for m in l_m:
        p.append(m.shape[0])
    p.append(l_m[len(l_m)-1].shape[1])
    m,s=mat_chain_order(p)
    return matrix_chain_multiply(l_m,s,0,len(l_m)-1)

def matrix_chain_multiply(a,s,i,j):
    if j==i:
        return a[i]
    else:
        a1=matrix_chain_multiply(a,s,i,int(s[i,j]))
        a2=matrix_chain_multiply(a,s,int(s[i,j])+1,j)
        return np.dot(a1,a2)

def tst():
    p=[30,35,15,5,10,20,25]
    m,s=mat_chain_order(p)
    print(m)
    print(s)
    print_opt_parenth(s,0,5)
    l_m = [np.ones((5,3)),np.ones((3,10)),\
       np.ones((10,7)),np.ones((7,5))]
    a = mult_matrices(l_m)
    print("\n\nNow, let's actually multiply the matrices\n")
    print(a)

