import numpy as np

def collect_water(a):
    i=0;j=len(a)-1
    max_i=a[i]; max_j=a[j]
    min_max = min(a[i],a[j])
    cnt=0
    while j>i:
        if max_i<max_j:
            i+=1
            max_i=max(max_i,a[i])
            min_max = min(max_j,max_i)
            if a[i]<min_max:
                cnt+=1
        else:
            j-=1
            max_j=max(max_j,a[j])
            min_max=min(max_i,max_j)
            if a[j]<min_max:
                cnt+=1
    return cnt+1

a=[0,1,2,1,0,1,2,3]
collect_water(a)

a=[0,-1,-2,-1]
collect_water(a)

def longest_valid_parenth(st):
    if st is None or st=="":
        return 0
    s_arr = np.array([ch for ch in st])
    n_arr = np.zeros(len(s_arr))
    n_arr[s_arr=='(']=-1
    n_arr[s_arr==')']=1
    n_arr = np.insert(n_arr,0,0)
    n_arr=np.cumsum(n_arr)
    return collect_water(n_arr)

st = "(()"
longest_valid_parenth(st)

st="))(()))"
longest_valid_parenth(st)

