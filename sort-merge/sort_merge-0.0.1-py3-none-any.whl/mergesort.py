import math

def merge_sort(a):
    '''
    Sorts the array a through Merge Sort Algo

    Parameters:
    a: array

    Returns:
    sorted array
    '''
    
    a = list(a)

    # If there's one element in array, no need to sort
    length = len(a)
    if length == 1:
        return a

    # Recursively splitting the array
    inter = [a]
    while len(inter) < len(a):
        temp = []
        for j in inter:
            i = int(math.ceil(len(j)/2))
            if len(j[:i]) != 0:
                temp.append(j[:i])
            if len(j[i:]) != 0:
                temp.append(j[i:])
        inter = temp

    # Recursively merging the array
    sorted_array = inter
    while len(sorted_array) != 1:
        temp = []
        for i in range(0, len(sorted_array), 2):
            if i+1 < len(sorted_array):
                m = merge(sorted_array[i], sorted_array[i+1])
                temp.append(m)
            else:
                m = merge(sorted_array[i])
                temp.append(m)
        
        sorted_array = temp

    return sorted_array[0]



def merge(a, b = None):
    '''
    Takes two sorted arrays and merges in a way that resultant array is sorted.
    If only one sorted array is passed, no merge needed and hence returns the passed array itself

    Parameters:
    a = sorted array1
    b = sorted array2

    Returns:
    res = merged sorted array
    '''   

    # If only one array is passed, no need for merge
    if b == None:
        return a

    p_a = 0 # pointer for array a
    p_b = 0 # pointer for array b
    res = []

    for _ in range(len(a) + len(b)):

        # Case 1: None of the two arrays has been looked up completely
        if p_a < len(a) and p_b < len(b):    

            # compares the elemnets in a and b, pointed by p_a and p_b respectively
            if a[p_a] <= b[p_b]:
                res.append(a[p_a])
                p_a += 1
            else:
                res.append(b[p_b])
                p_b += 1

        # Case 2: If array b has been completely looked up
        elif p_a < len(a) and p_b >= len(b):        
            res.append(a[p_a])
            p_a += 1
        
        # Case 3: If array a has been completely looked up
        else:             
            res.append(b[p_b])
            p_b += 1

    return res

