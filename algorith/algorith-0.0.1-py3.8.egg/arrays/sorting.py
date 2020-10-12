import numpy as np
from importlib import reload


class MergeSort():
    def __init__(self,a):
        self.arr=a
    
    @staticmethod
    def merge(a1,a2):
        a=np.zeros(len(a1)+len(a2))
        i=0; j=0; k=0
        while i<len(a1) or j<len(a2):
            if i<len(a1) and (j==len(a2) or a1[i]<a2[j]):
                a[k] = a1[i]
                k+=1
                i+=1
            elif j<len(a2) and (i==len(a1) or a1[i]>=a2[j]):
                a[k] = a2[j]
                k+=1
                j+=1
        return a

    @staticmethod
    def merge2(a,i1,i2,j1,j2):
        return 1
    
    @staticmethod
    def mergesort(a):
        return 1

## Counting inversions.
## Sorting linked lists doesn't even require extra space.

class QuickSort():
    def __init__(self,a):
        self.arr=a


