import numpy as np






############################################
class FailedAttempts():
    ##Failed attempts based on max water.
    @staticmethod
    def collect_water(a):
        i=0;j=len(a)-1
        min_ix=len(a)-1; max_ix=0
        max_i=a[i]; max_j=a[j]
        min_max = min(a[i],a[j])
        while j>i:
            if max_i<max_j:
                i+=1
                max_i=max(max_i,a[i])
                min_max = min(max_j,max_i)
                if a[i]<min_max:
                    min_ix=min(min_ix,i)
                    max_ix=max(max_ix,i)
            else:
                j-=1
                max_j=max(max_j,a[j])
                min_max=min(max_i,max_j)
                if a[j]<min_max:
                    min_ix=min(min_ix,j)
                    max_ix=max(max_ix,j)
        return max_ix-min_ix+2

    @staticmethod
    ##Incomplete.
    def collect_water_2(a):
        maxs_from_left=[]
        max_from_left=-np.inf
        for i in a:
            if max_from_left<i:
                max_from_left=i
            maxs_from_left.append(max_from_left)
        maxs_from_right=[]
        max_from_right=-np.inf
        for i in np.arange(len(a)-1,-1,-1):
            if max_from_right<a[i]:
                max_from_right=a[i]
            maxs_from_right.append(max_from_right)
        min_maxs = []
        for i in range(len(a)):
            min_maxs.append(min(maxs_from_right[i],\
                        maxs_from_left[i]))

    @staticmethod
    def tst():
        a=[0,1,2,1,0,1,2,3]
        FailedAttempts.collect_water(a)

        a=[0,-1,-2,-1]
        FailedAttempts.collect_water(a)

    @staticmethod
    def longest_valid_parenth(st):
        if st is None or st=="":
            return 0
        s_arr = np.array([ch for ch in st])
        n_arr = np.zeros(len(s_arr))
        n_arr[s_arr=='(']=-1
        n_arr[s_arr==')']=1
        n_arr = np.insert(n_arr,0,0)
        n_arr=np.cumsum(n_arr)
        return FailedAttempts.collect_water(n_arr)

    @staticmethod
    def tst2():
        st = "(()"
        FailedAttempts.longest_valid_parenth(st)

        st="))(()))"
        FailedAttempts.longest_valid_parenth(st)

        st=")()())"
        FailedAttempts.longest_valid_parenth(st)




