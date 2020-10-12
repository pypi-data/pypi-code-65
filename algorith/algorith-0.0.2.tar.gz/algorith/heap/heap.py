import heapq as hq
import numpy as np

class Heap():
    def __init__(self):
        self.h_arr = []
        self.size = 0
    
    def pop(self):
        self.size-=1
        return hq.heappop(self.h_arr)

    def push(self,i):
        self.size += 1
        return hq.heappush(self.h_arr,i)

    def peek(self):
        if len(self.h_arr)>0:
            return hq.nsmallest(1,self.h_arr)[0]
        else:
            return np.inf

