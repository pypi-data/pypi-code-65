import numpy as np

def print_paths(n,start,end,arr):
    if start[0]-end[0]==-1 and start[1]-end[1]==1:
        arr.append(')')
        print(''.join(arr))
    elif sum(start)==2*n:
        arr.append(')')
        start+=np.array([1,-1])
        print_paths(n,start,end,arr)
    elif start[1] == 0:
        arr.append('(')
        start+=np.array([1,1])
        print_paths(n,start,end,arr)
    else:
        arr_up = arr.copy()
        arr_down=arr.copy()
        arr_up.append('(')
        start1=start+np.array([1,1])
        print_paths(n,start1,end,arr_up)        
        arr_down.append(')')
        start2=start+np.array([1,-1])
        print_paths(n,start2,end,arr_down)

def tst(n):
    start=np.array([0,0])
    end=np.array([2*n,0])
    arr=[]
    print_paths(n,start,end,arr)

