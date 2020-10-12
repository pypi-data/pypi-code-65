import numpy as np
import pandas as pd
import heapq as hq


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

    def peak(self):
        if len(self.h_arr)>0:
            return hq.nsmallest(1,self.h_arr)[0]
        else:
            return np.inf


def down_intervals(starts, ends):
    heap = Heap()
    r_starts=[]; r_ends=[]; start_app=True
    downs = []
    down = 0
    for i in range(len(starts)):
        start_app = update_arrays(starts[i],r_starts,r_ends,start_app)
        while heap.size>0 and starts[i] > heap.peak():
            entry=heap.pop()
            start_app = update_arrays(entry,r_starts,r_ends,start_app)
            down-=1
            downs.append(down)
        heap.push(ends[i])
        down+=1
        downs.append(down)
    ##In the end, the heap should have only one element left.
    while heap.size > 1:
        entry=heap.pop()
        start_app = update_arrays(entry,r_starts,r_ends,start_app)
        down-=1
        downs.append(down)
    ##TODO: Fix the r_starts and r_ends arrays.
    return downs#, r_starts, r_ends


def update_arrays(entry,r_starts,r_ends,start_app):
    if start_app:
        r_starts.append(entry)
    else:
        r_ends.append(entry)
    return not start_app


def complete_intervals(df):
    downs = down_intervals(np.array(df['start']),np.array(df['end']))
    ##TODO: This sorting is O(nlog(n)). We can take start and end times
    # from the down_intervals logic itself. Then, the code will be O(n).
    # where n is the number of rows in the data-frame.
    all_intervals = np.sort(np.concatenate((np.array(df['start']),\
                np.array(df['end'])),axis=0))
    ends = all_intervals[1:]
    starts = all_intervals[:len(all_intervals)-1]
    d={'start':starts,'end':ends,'vms_down':downs}
    return pd.DataFrame(d)


def tst_cases():
    d = {'start': [0,1,2,4,12], 'end': [10,3,6,5,13]}
    df = pd.DataFrame(data=d)
    starts = np.array([7229.47528991, 7897.40169628, 7982.13448482, 8278.92599446,
        8537.09051065, 8840.41211186, 9292.70526944])

    ends = np.array([7872.99517439, 9809.11542893, 8436.9128489 , 8859.04535374,
        8663.99877008, 9056.34406511, 9943.38234052])
    ends = ends-min(starts)
    starts = starts-min(starts)

    downs = down_intervals(starts,ends)
    downs_actual = [1,0,1,2,3,2,3,4,3,2,1,2,1]

    starts = np.array([7160.10222095, 8725.82215193, 8974.77659027, 9434.74089778])
    ends = np.array([8580.92427663, 9246.29447802, 8978.89139938, 9745.52277918])
    ends = ends-min(starts)
    starts = starts-min(starts)

    downs = down_intervals(starts,ends)
    downs_actual = np.array([1, 0, 1, 2, 1, 0, 1])

