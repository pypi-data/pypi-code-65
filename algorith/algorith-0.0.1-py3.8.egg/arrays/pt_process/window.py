import numpy as np

def critical_interval(ts1,w,delt):
    t_end_prev=0
    critical=0
    for t1 in ts1:
        t_start=min(t1,t1+w)
        t_start=max(t_start,0)
        t_end=max(t1,t1+w)
        t_end=min(t_end,delt)
        t_start=max(t_start,t_end_prev)
        critical+=(t_end-t_start)
        t_end_prev=t_end
    return critical


def tst_critical_interv():
    ##### For critical interval.
    res = critical_interval([1,2,3],1,4)
    print(res==3)
    res = critical_interval([1,3],-5,4)
    print(res==3)
    res = critical_interval([1,3],-5,4)
    print(res==3)
    res = critical_interval([1,3],1,4)

