import numpy as np


def max_water(a):
    i=0;
    j=len(a)-1;
    max_ar=0
    while j>i:
        ar=min(a[j],a[i])*(j-i)
        if ar>max_ar:
            max_ar=ar
        if a[j]<a[i]:
            j-=1
        else:
            i+=1
    return max_ar

a=[1,8,6,2,5,4,8,3,7]
max_water(a)

a=[3,2,5,25,24,5]
max_water(a)

