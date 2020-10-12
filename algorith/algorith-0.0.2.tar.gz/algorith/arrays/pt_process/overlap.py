import numpy as np
import time
from algorith.arrays.binary_srch import binary_search, binary_search_oprns


def critical_events(ts1,ts2,w):
    """
    ts1 rains down upon ts2. The window size can be 
    positive or negative.
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
    if w>0:
        return critical_events_v2_pos_w(ts1,ts2,w)
    elif w<0:
        return critical_events_v2_neg_w(ts1,ts2,w)
    else:
        return 0


def critical_events_v2_neg_w(ts1,ts2,w):
    """
    Designed for when ts1 is much larger than ts2.
    Leverages binary search to find critical events
    from ts1 lying within w-window of some event in ts2
    in O(mlog(n)) time where m=len(ts2), n=len(ts1)
    params:
        ts1: The first array, raining down on ts2.
        ts2: The second array around which we find intervals.
        w: The window size. Must be negative for this method.
    """
    critical=0; ix=len(ts1)-1; seen_until=len(ts1)
    for ii in range(len(ts2)-1,-1,-1):
        t=ts2[ii]
        ix=binary_search(ts1,t,0,ix)
        seen_until=min(seen_until,ix+1)
        while ix>-1 and t+w<ts1[ix]:
            # The binary search has a propensity to 
            # go forward. So, we avoid double counting.
            critical+=(seen_until>ix)
            ix-=1            
            seen_until=min(seen_until,ix+1)
    return critical


def critical_events_v2_pos_w(ts1,ts2,w):
    """
    Designed for when ts1 is much larger than ts2.
    Leverages binary search to find critical events
    from ts1 lying within w-window of some event in ts2
    in O(mlog(n)) time where m=len(ts2), n=len(ts1)
    params:
        ts1: The first array, raining down on ts2.
        ts2: The second array around which we find intervals.
        w: The window size. Must be positive for this method.
    """
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


def critical_events_v3_pos_w(ts1,ts2,w):
    eta=0; start=-1; end=len(ts1)-1
    for t in ts2:
        i1 = binary_search(ts1,t,max(0,start),end)
        i1=max(i1,start)
        i2 = binary_search(ts1,t+w,max(0,i1),end)
        i2=max(i2,start)
        eta+=(i2-i1)
        start=max(start,i2)
        if start>=len(ts1)-1:
            return eta
    return eta



def critical_events_v3_pos_w_oprns(ts1,ts2,w,oprns=[0]):
    eta=0; start=-1; end=len(ts1)-1
    for t in ts2:
        i1 = binary_search_oprns(ts1,t,max(0,start),end,oprns=oprns)
        i1=max(i1,start)
        oprns[0]+=1
        i2 = binary_search_oprns(ts1,t+w,max(0,i1),end,oprns=oprns)
        i2=max(i2,start)
        eta+=(i2-i1)
        start=max(start,i2)
        oprns[0]+=3
        if start>=len(ts1)-1:
            oprns[0]+=1
            return eta
    return eta


def critical_events_v3(ts1,ts2,w):
    if w>0:
        return critical_events_v3_pos_w(ts1,ts2,w)
    else:
        ## TODO: Implement v3 version for negative w.
        return critical_events_v2_neg_w(ts1,ts2,w)


def critical_events_v4_pos_w(ts1,ts2,w):
    st1=-1; st2=0
    eta=0
    while (st1<len(ts1)-1) and (st2<len(ts2)):
        i1 = binary_search(ts1,ts2[st2],max(st1,0),len(ts1)-1)
        i1=max(st1,i1)
        i2 = binary_search(ts1,ts2[st2]+w,max(i1,0),len(ts1)-1)
        i2=max(st1,i2)
        eta+=(i2-i1)
        st1 = max(st1,i2)
        if st1<len(ts1)-1:
            st2_pr=binary_search(ts2,ts1[st1+1],st2+1,len(ts2)-1)
            st2=max(st2_pr,st2+1)
    return eta


def critical_events_v4(ts1,ts2,w):
    if w>0:
        return critical_events_v4_pos_w(ts1,ts2,w)
    else:
        ## TODO: Implement v4 version for negative w.
        return critical_events_v2_neg_w(ts1,ts2,w)


def functional_tst():
    ## Test cases.
    ev = critical_events_v2([.5,1.5,2.5],[1,2,3],.45)
    print(ev==0)
    ev = critical_events_v2([1.4,1.4,2.7],[1,2,3],.5)
    print(ev==2)
    ev = critical_events_v2([1.4,2.4,3.4],[1,2,3],.5)
    print(ev==3)
    ev = critical_events([1,2,3],[.5,1.5,2.5],-1)
    print(ev==3)
    ev = critical_events([1,2,3],[.5,1.5,2.5],1)
    print(ev==3)
    ## From a simulation.
    ts1=np.array([0.02364078, 0.05228936, 0.3201887 , 
        0.41696722, 0.50680057, 0.58062848, 0.6491584 , 0.76480126, 
        0.79478828, 0.9453893 ])
    ts2=np.array([0.24825007, 0.70216959, 0.73216372, 0.89533743, 0.97304893])
    ev=critical_events_v2(ts1,ts2,0.1)
    print(ev==4)
    ev=critical_events_v2(ts1,ts2,-0.1)
    print(ev==2)


def scale_tst():
    ts1=np.sort(np.random.uniform(size=500000))
    ts2=np.sort(np.random.uniform(size=100))
    start = time.time()
    crit1 = critical_events(ts1,ts2,0.0001)
    end = time.time()
    print(crit1)
    print(end - start)
    start = time.time()
    crit2 = critical_events_v2(ts1,ts2,0.0001)
    end = time.time()
    print(crit2)
    print(end - start)
    print("Functional test result: " + str(crit2==crit1))



