
def binary_search(a, d, lo, hi, asc_order=True):
    if a[lo]>d:
        return lo-1
    elif a[hi]<d:
        return hi
    while lo < hi:
        mid = (lo+hi)//2
        midval = a[mid]
        if midval < d:
            if asc_order:
                lo = mid+1
            else:
                hi = mid-1
        elif midval > d:
            if asc_order:
                hi = mid-1
            else:
                lo = mid+1
        else:
            return mid
    if a[lo]<=d:
        return lo
    else:
        return int(lo-(asc_order-0.5)*2)


def binary_search_oprns(a, d, lo, hi, asc_order=True,\
                        oprns=[0]):
    """
    Binary search, but counts the 
    number of operations for complexity analysis.
    """
    if a[lo]>d:
        oprns[0]+=1
        return lo-1
    elif a[hi]<d:
        oprns[0]+=1
        return hi
    while lo < hi:
        oprns[0]+=1
        mid = (lo+hi)//2
        oprns[0]+=1
        midval = a[mid]
        if midval < d:
            oprns[0]+=1
            if asc_order:
                lo = mid+1
            else:
                hi = mid-1
        elif midval > d:
            oprns[0]+=1
            if asc_order:
                hi = mid-1
            else:
                lo = mid+1
        else:
            return mid
    if a[lo]<=d:
        oprns[0]+=1
        return lo
    else:
        return int(lo-(asc_order-0.5)*2)


def tst():
    re = binary_search([1,2,3,4,5],2.6,0,4)
    print("Test-1: "+str(re==1))


