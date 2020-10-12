import numpy as np
from algorith.arrays.binary_srch import binary_search
import pandas as pd



def critical_events_per_object_v2(ts1_df,ts2_df,w):
    """
    Slow as pig even for intermediate w.
    """
    ts1_df=ts1_df.sort_values(by=['RelativeTime'])
    ts2_df=ts2_df.sort_values(by=['RelativeTime'])
    ts1=np.array(ts1_df.RelativeTime)
    ts2=np.array(ts2_df.RelativeTime)
    nodes1=np.array(ts1_df.NodeId)
    nodes2=np.array(ts2_df.NodeId)
    critical_arr=np.zeros(len(ts1))
    ix=0
    for i in range(len(ts2)):
        t=ts2[i]
        node2=nodes2[i]
        ix=binary_search(ts1,t,ix,len(ts1)-1)
        ix1=ix
        while ix1+1<len(ts1) and t+w>ts1[ix1+1]:
            node1=nodes1[ix1+1]
            critical_arr[ix1+1]+=(node2==node1)
            ix1+=1
    return sum(critical_arr>0)


def tsts():
    ts1=np.array([0.02364078, 0.05228936, 0.3201887 , 
            0.41696722, 0.50680057, 0.58062848, 0.6491584 , 0.76480126, 
            0.79478828, 0.9453893 ])
    nodes1=np.array(["ffff3803-ff85-425f-ac60-9c37a5914eee" for i in range(len(ts1))])

    ts2=np.array([0.24825007, 0.70216959, 0.73216372, 0.89533743, 0.97304893])
    nodes2=np.array(["ffff3803-ff85-425f-ac60-9c37a5914eee" for i in range(len(ts2))])

    ts1_df=pd.DataFrame({"NodeId":nodes1,"RelativeTime":ts1})
    ts2_df=pd.DataFrame({"NodeId":nodes2,"RelativeTime":ts2})

    ev=critical_events_per_object_v2(ts1_df,ts2_df,0.1)
    print(ev==4)

    ts1_1=np.array([1.4,1.4,2.7])
    nodes1_1=np.array(["512946a9-b3a6-40d3-991d-aa831a883eb1" for i in range(len(ts1_1))])

    ts2_1=np.array([1,2,3])
    nodes2_1=np.array(["512946a9-b3a6-40d3-991d-aa831a883eb1" for i in range(len(ts2_1))])

    ts1_df1=pd.DataFrame({"NodeId":nodes1_1,"RelativeTime":ts1_1})
    ts2_df1=pd.DataFrame({"NodeId":nodes2_1,"RelativeTime":ts2_1})

    ts1_df=pd.concat([ts1_df,ts1_df1])
    ts2_df=pd.concat([ts2_df,ts2_df1])

    ev=critical_events_per_object_v2(ts1_df,ts2_df,0.1)
