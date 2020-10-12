import numpy as np


def two_median(a1,a2):
    m=len(a1); n=len(a2)
    if m==0 and n>0:
        return np.median(a2)
    if n==0 and m>0:
        return np.median(a1)
    if m==0 and n==0:
        raise Exception("Both arrays can't be empty!")
    if m==n:
        if a1[m-1]<a2[m-1]:
            return (two_indexer(a2,a1,1,m-1,1,m,m)+\
                        two_indexer(a2,a1,1,m-1,1,m,m+1))/2
        else:
            return (two_indexer(a1,a2,1,m-1,1,m,m)+\
                        two_indexer(a1,a2,1,m-1,1,m,m+1))/2
    if (m+n)%2==1:
        if m>n:
            return two_indexer(a2,a1,1,n,1,m,int((m+n)/2)+1)
        else:
            return two_indexer(a1,a2,1,m,1,n,int((m+n)/2)+1)
    else:
        if m>n:
            return (two_indexer(a2,a1,1,n,1,m,int((m+n)/2)+1)+\
                    two_indexer(a2,a1,1,n,1,m,int((m+n)/2)))/2
        else:
            return (two_indexer(a1,a2,1,m,1,n,int((m+n)/2)+1)+\
                    two_indexer(a1,a2,1,m,1,n,int((m+n)/2)))/2


def two_indexer(a1,a2,i1,i2,j1,j2,r):
    m=i2-i1+1
    n=j2-j1+1
    if n<=m:
        raise Exception("Require second array to be larger.")
    if n>r:
        j2-=(n-r)
    if m<r:
        j1+=(r-m-1)
        r = m+1
    while i2>i1 and j2>j1:
        p_1 = i1+int((i2-i1)/2)+1
        #p_2 = int((j1+j2)/2)
        n_s = n_smaller(a1[p_1-1],a2,j1,j2)
        r_x = min(p_1-i1+n_s+1,(i2-i1+1)+(j2-j1+1))
        if r == r_x:
            print("Found it!")
            return a1[p_1-1]
        elif r_x > r:
            i2=max(p_1-1,1)
            if n_s < j2-j1+1:
                j2 = j1+n_s-1
        else:
            i1 += 1
            j1 += n_s
            r -= (n_s+1)
        if r == (i2-i1+1)+(j2-j1+1):
            return max(a1[i2-1],a2[j2-1])
        if r == 1:
            return min(a1[i1-1],a2[j1-1])
    if i1==i2:
        return array_num_median(a1[i1-1],a2,r,j1,j2)
    if j1==j2:
        return array_num_median(a2[j1],a1,r,i1,i2)


def n_smaller(num,a,i1,i2):
    """
    Returns the number of elements smaller
    than num in sorted array, a between indices 
    i1 and i2
    """
    if num>a[i2-1]:
        return i2-i1+1
    elif num<a[i1-1]:
        return 0
    hi=i2-1; lo=i1-1
    mid = int((lo+hi)/2)
    while hi>lo:
        if num==a[mid] or hi-lo<=1:
            return mid+1-i1+1
        elif num>a[mid]:
            lo=mid
        else:
            hi=mid
        mid = int((lo+hi)/2)
    return lo+1-i1+1


def array_num_median(num,a,req_ix,ix1,ix2):
    n_s=n_smaller(num,a,ix1,ix2)
    if n_s==req_ix-1:
        return num
    elif n_s<req_ix-1:
        return a[ix1+(req_ix-1)-2]
    else:
        return a[ix1+(req_ix-1)-1]

###Some tests..
#########################
def base_tst():
    a11=np.array([ 3,  6,  8, 11, 13, 14])
    a21=np.array([ 0,  1,  2,  4,  5,  7,  9, 10, 12])
    mm1 = two_indexer(a11,a21,1,len(a11),1,len(a21),8)
    print(mm1)


def tst(n_e):
    a = np.arange(n_e)
    mm = np.median(a)
    nn = np.random.choice(n_e)
    ix = np.random.choice(n_e,size=nn,replace=False)
    a2=np.delete(a,ix)
    ix.sort()
    a1=ix
    if len(a1)<len(a2):
        mm1=two_indexer(a1,a2,1,len(a1),1,len(a2),int(len(a)/2)+1)
    elif len(a1)>len(a2):
        mm1=two_indexer(a2,a1,1,len(a2),1,len(a1),int(len(a)/2)+1)
    print(mm1)
    print(mm)


def tst_median(n_e):
    a = np.arange(n_e)
    mm = np.median(a)
    nn = np.random.choice(n_e)
    ix = np.random.choice(n_e,size=nn,replace=False)
    a2=np.delete(a,ix)
    ix.sort()
    a1=ix
    mm1 = two_median(a1,a2)
    print(mm1)
    print(mm)
