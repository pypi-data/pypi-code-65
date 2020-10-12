import numpy as np
import pandas as pd
from algorith.heap.heap import Heap
from algorith.arrays.birth_death.down_instance import DownInstance


def num_down(starts, ends):
    """
    Gets number of instances down in sequence given start and end times 
    of down intervals in arrays. All other functions here are
    mutations of this that address related tasks.
    """
    heap = Heap()
    downs = []
    down = 0
    for i in range(len(starts)):
        while heap.size>0 and starts[i] > heap.peek():
            heap.pop()
            down-=1
            downs.append(down)
        heap.push(ends[i])
        down+=1
        downs.append(down)
    ##In the end, the heap should have only one element left.
    while heap.size > 1:
        heap.pop()
        down-=1
        downs.append(down)
    return downs


def num_down_w_times(starts, ends):
    """
    Get the number of down machiens and timestamps
    at which state changes happen. A dataframe can be created
    via the code in complete_intervals for starts and ends.
    """
    heap = Heap()
    downs = []
    time_stamps = []
    down = 0
    for i in range(len(starts)):
        while heap.size>0 and starts[i] > heap.peek():
            entry=heap.pop()
            time_stamps.append(entry)
            down-=1
            downs.append(down)
        time_stamps.append(starts[i])
        heap.push(ends[i])
        down+=1
        downs.append(down)
    ##In the end, the heap should have only one element left.
    while heap.size > 1:
        entry=heap.pop()
        time_stamps.append(entry)
        down-=1
        downs.append(down)
    time_stamps.append(heap.pop())
    return np.array(downs), np.array(time_stamps)


def num_down_w_times_v1(starts,ends,n_downs):
    """
    Same as num_down_w_times, except takes the number of down machines
    into account as a third input array. If the downs array is all 1's,
    it is equivalent to num_down_w_times.
    """
    heap=Heap()
    downs = []
    time_stamps = []
    down = 0
    for i in range(len(starts)):
        while heap.size>0 and starts[i] > heap.peek().end_time:
            entry=heap.pop()
            time_stamps.append(entry.end_time)
            down-=entry.down
            downs.append(down)
        time_stamps.append(starts[i])
        heap.push(DownInstance(ends[i],n_downs[i]))
        down+=n_downs[i]
        downs.append(down)
    while heap.size>1:
        entry=heap.pop()
        time_stamps.append(entry.end_time)
        down-=entry.down
        downs.append(down)
    time_stamps.append(heap.pop().end_time)
    return np.array(downs), np.array(time_stamps)


def system_downs(starts, ends, d):
    """
    Given that the system is down when d or more
    machines are down, produces the intervals when
    the system is down. In a k of n system, d=(n-k+1)
    """
    heap = Heap()
    is_down=False
    downs = []
    time_stamps = []
    down = 0
    for i in range(len(starts)):
        while heap.size>0 and starts[i] > heap.peek():
            entry=heap.pop()
            down-=1
            if down<d and is_down:
                is_down=False
                downs.append(0)
                time_stamps.append(entry)
        heap.push(ends[i])
        down+=1
        if down>=d and not is_down:
            is_down = True
            downs.append(1)
            time_stamps.append(starts[i])        
    ##In the end, the heap should have only one element left.
    while heap.size > 1:
        entry=heap.pop()
        down-=1
        if down<d and is_down:
            is_down = False
            downs.append(0)
            time_stamps.append(entry)
    time_stamps.append(heap.pop())
    return np.array(downs), np.array(time_stamps)


def system_downs_v1(starts, ends, n_downs, d):
    """
    Same as system_downs, except takes the number of down machines
    into account as a third input array. If the downs array is all 1's,
    it is equivalent to system_downs.
    """
    heap = Heap()
    is_down=False
    downs = []
    time_stamps = []
    down = 0
    for i in range(len(starts)):
        while heap.size>0 and starts[i] > heap.peek().end_time:
            entry=heap.pop()
            down-=entry.down
            if down<d and is_down:
                is_down=False
                downs.append(0)
                time_stamps.append(entry.end_time)
        heap.push(DownInstance(ends[i],n_downs[i]))
        down+=n_downs[i]
        if down>=d and not is_down:
            is_down = True
            downs.append(1)
            time_stamps.append(starts[i])        
    ##In the end, the heap should have only one element left.
    while heap.size > 1:
        entry=heap.pop()
        down-=entry.down
        if down<d and is_down:
            is_down = False
            downs.append(0)
            time_stamps.append(entry.end_time)
    time_stamps.append(heap.pop().end_time)
    return np.array(downs), np.array(time_stamps)


def complete_intervals(df):
    downs = num_down(np.array(df['start']),np.array(df['end']))
    ##TODO: This sorting is O(nlog(n)). We can take start and end times
    # from the num_down logic itself. Then, the code will be O(n).
    # where n is the number of rows in the data-frame.
    all_intervals = np.sort(np.concatenate((np.array(df['start']),\
                np.array(df['end'])),axis=0))
    ends = all_intervals[1:]
    starts = all_intervals[:len(all_intervals)-1]
    ## TODO: remove vms_down. Maintained for now for backward compatibility.
    d={'start':starts,'end':ends,'vms_down':downs,'down':downs}
    return pd.DataFrame(d)


def system_down_intervals(starts, ends, d):
    ds,ts=system_downs(starts, ends, d)
    ends = ts[1:]
    starts = ts[:len(ts)-1]
    d={'start':starts,'end':ends,'down':ds}
    return pd.DataFrame(d)


def tst_cases():
    d = {'start': [0,1,2,4,12], 'end': [10,3,6,5,13]}
    df = pd.DataFrame(data=d)
    ## If you're Rohit, see One/Topics/CS/BirthDeath/TestCases. Else nevermind.
    starts1 = np.array([7229.47528991, 7897.40169628, 7982.13448482, 8278.92599446,
        8537.09051065, 8840.41211186, 9292.70526944])

    ends1 = np.array([7872.99517439, 9809.11542893, 8436.9128489 , 8859.04535374,
        8663.99877008, 9056.34406511, 9943.38234052])
    ends1 = ends1-min(starts1)
    starts1 = starts1-min(starts1)

    downs = num_down(starts1,ends1)
    downs_actual = [1,0,1,2,3,2,3,4,3,2,1,2,1]
    ds,ts=num_down_w_times(starts1,ends1)
    ds,ts=system_downs(starts1,ends1,2)
    ds,ts=system_downs(starts1,ends1,1)

    starts2 = np.array([7160.10222095, 8725.82215193, 8974.77659027, 9434.74089778])
    ends2 = np.array([8580.92427663, 9246.29447802, 8978.89139938, 9745.52277918])
    ends2 = ends2-min(starts2)
    starts2 = starts2-min(starts2)

    downs = num_down(starts2,ends2)
    downs_actual = np.array([1, 0, 1, 2, 1, 0, 1])
    ds,ts=num_down_w_times(starts2,ends2)
    ds,ts=system_downs(starts2,ends2,2)
    ds,ts=system_downs(starts2,ends2,1)

    downs1 = np.ones(len(starts1))*2
    ds,ts=num_down_w_times_v1(starts1,ends1,downs1)
    ds,ts=system_downs_v1(starts1,ends1,downs1,3)

