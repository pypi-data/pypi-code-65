# merge.py

def merge_increasing(lst: list, L: list, R: list):
    """
    `merege_increasing` merges two sorted sub-lists into their original list input in 
    increasing order. It takes three lists, original, right-hand sub-list, and 
    left-hand sub-list. The function returns None.
    """

    i = j = k = 0 #initialize indices

    while i < len(L) and j < len(R): #iterate while neither sub-list has exhausted their index

        if L[i] < R[j]: #compare next set of values

            lst[k] = L[i] #overwrite input list

            i+=1 #increment Left sub-list index

        else:

            lst[k] = R[j] #overwrite

            j+=1 #increment
            
        k+=1
    
    while i < len(L): #loop over remaining left sub-list indices if existent

        lst[k] = L[i] #overwrite

        i+= 1

        k+= 1
    
    while j < len(R): #loop over remaining right sub-list indices if existent

        lst[k] = R[j] #overwrite

        j+= 1

        k+= 1


def merge_decreasing(lst: list, L: list, R: list):
    """
    `merge_decreasing` merges two sorted sub-lists into their original list input in 
    decreasing order. It takes three lists, original, right-hand sub-list, and 
    left-hand sub-list. The function returns None.
    """
    i = j = k = 0 #initialize indices

    while i < len(L) and j < len(R): #iterate while neither sub-list has exhausted their index

        if L[i] > R[j]: #compare next set of values

            lst[k] = L[i] #overwrite input list

            i+=1 #increment Left sub-list index

        else:

            lst[k] = R[j] #overwrite

            j+=1 #increment
            
        k+=1
    
    while i < len(L): #loop over remaining left sub-list indices if existent

        lst[k] = L[i] #overwrite

        i+= 1

        k+= 1
    
    while j < len(R): #loop over remaining right sub-list indices if existent

        lst[k] = R[j] #overwrite

        j+= 1
        
        k+= 1


def merge(lst: list, increasing=True):
    """`merge` is an implementation of the merge-sort algorithm. It takes a list argument 
    and returns None, sorting the input instead. Optional param `increasing` dictates the 
    algorithm's sorting order and is set to True by default.
    """

    if len(lst) > 1:

        mid = len(lst) // 2     # define midpoint
        L = lst[:mid]   # temporary left sub-list
        R = lst[mid:]   # temporary right sub-list

        merge(L, increasing) #merge left sub-list
        merge(R, increasing) #merge right sub-list

        if increasing: #check sorted-order param

            merge_increasing(lst, L, R) #sort increasing

        else:

            merge_decreasing(lst, L, R) #sort decreasing