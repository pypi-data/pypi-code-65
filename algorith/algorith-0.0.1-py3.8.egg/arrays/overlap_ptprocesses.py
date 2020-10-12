import numpy as np
import time
from algorith.arrays.binary_srch import binary_search


def critical_events(ts1,ts2,w):
    """
    ts1 rains down upon ts2.
    """
    if len(ts2)==0 or len(ts1)==0:
        return 0
    j=0; critical=0
    for t in ts1:
        #First time an entry in ts2 crosses
        #current entry of ts1
        # ts2[j-1].....t......ts2[j]
        while j<len(ts2) and t>ts2[j]:
            j+=1
        if w>0 and j>0:
            critical+=(ts2[j-1]+w>t)
        elif j<len(ts2) and w<0:
            critical+=(ts2[j]+w<t)
    return critical


def critical_events_v2(ts1,ts2,w):
    critical=0; ix=0; seen_until=-1
    for t in ts2:        
        ix=binary_search(ts1,t,ix,len(ts1)-1)
        seen_until=max(seen_until,ix)
        while ix+1<len(ts1) and t+w>ts1[ix+1]:
            # The binary search has a propensity to 
            # go backwards. So, we avoid double counting.
            critical+=(seen_until<(ix+1))
            ix+=1            
            seen_until=max(seen_until,ix)
    return critical


def functional_tst():
    ## Test cases.
    ev = critical_events_v2([.5,1.5,2.5],[1,2,3],.5)
    print(ev==0)
    ev = critical_events_v2([1.4,1.4,2.7],[1,2,3],.5)
    print(ev==2)
    ev = critical_events_v2([1.4,2.4,3.4],[1,2,3],.5)
    print(ev==3)
    ts1=np.array([0.02364078, 0.05228936, 0.3201887 , 0.41696722, 0.50680057,
        0.58062848, 0.6491584 , 0.76480126, 0.79478828, 0.9453893 ])
    ts2=np.array([0.24825007, 0.70216959, 0.73216372, 0.89533743, 0.97304893])
    ev=critical_events_v2(ts1,ts2,0.1)
    print(ev==4)


def scale_tst():
    ts1=np.sort(np.random.uniform(size=500000))
    ts2=np.sort(np.random.uniform(size=100))
    start = time.time()
    crit = critical_events(ts1,ts2,0.0001)
    end = time.time()
    print(crit)
    print(end - start)
    start = time.time()
    crit = critical_events_v2(ts1,ts2,0.0001)
    end = time.time()
    print(crit)
    print(end - start)


