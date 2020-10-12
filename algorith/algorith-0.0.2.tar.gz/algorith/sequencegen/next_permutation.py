import numpy as np
from math import factorial
import algorith.clr_book.ch12_binary_srch_trees.tree as tr

def permutation_to_num(arr):
    so_far = []
    n=len(arr)
    res=0
    fac = factorial(n)
    for i in range(len(arr)):
        fac/=n-i
        res+=(arr[i]-1-more_than_so_far(so_far,arr[i]))\
            *fac
        so_far.append(arr[i])
    return int(res)

def num_to_permutation(a,n):
    res = []
    so_far = [i for i in range(n)]
    fac = factorial(n)
    for i in range(n):
        fac/=n-i
        tmp = int(a//fac)     
        res.append(int(so_far[tmp]+1))
        ##O(n) operation on average
        so_far.pop(tmp)
        a=a%fac
    return res


def more_than_so_far(so_far,a):
    cumulative=0
    for i in so_far:
        if i<=a:
            cumulative+=1
    return cumulative

def permutation_to_num_v2(arr):
    n=len(arr)
    res=0
    tn=tr.TreeNode(arr[0],None,None); more_than=0
    trr=tr.Tree(tn)
    fac = factorial(n)
    for i in range(len(arr)):
        if i>0:
            tn_tmp = tr.TreeNode(arr[i],None,None)
            more_than = trr.insert(tn_tmp)
        fac/=n-i
        res+=(arr[i]-1-more_than)*fac
    return int(res)

def num_to_permutation_v2(a,n):
    res = []
    fac = factorial(n)
    tn=tr.TreeNode(a//(fac/n),None,None); more_than=0
    trr=tr.Tree(tn)    
    for i in range(n):
        fac/=n-i
        tmp = a//fac
        if i>0:
            tn_tmp = tr.TreeNode(tmp,None,None)
            more_than = trr.insert(tn_tmp)        
        res.append(int(tmp+1+more_than))
        a=a%fac
    return res

def next_permutation(arr):
    arr2=np.arange(len(arr))+1
    permut = [x for _,x in sorted(zip(arr,arr2))]
    while True:
        n=permutation_to_num_v2(permut)
        n=(n+1)%factorial(len(arr))
        permut = num_to_permutation(n,len(arr))
        res_arr = [arr[i] for i in np.array(permut)-1]
        for i in range(len(res_arr)):
            if arr[i] != res_arr[i]:
                return res_arr


#def tst():
arr = [1,2,4,3]
num1=permutation_to_num(arr)
num2=permutation_to_num_v2(arr)

num=21
a1=num_to_permutation(num,4)

#a2=num_to_permutation_v2(num,4)

