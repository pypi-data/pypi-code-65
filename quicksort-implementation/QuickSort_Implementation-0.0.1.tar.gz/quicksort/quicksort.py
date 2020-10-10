def partition(arr, l, r):
    '''
    Partition 
    '''
    ls = l
    pivot = arr[ls]
    for i in range(l + 1, r+1):
        if arr[i] < pivot:
            l = l + 1
            temp = arr[l]
            arr[l] = arr[i]
            arr[i] = temp
   
    temp = arr[ls] 
    arr[ls] = arr[l]
    arr[l] = temp
    return l

def quick_sort(arr, l, r):
    '''
    Quicksort
    '''
    if l < r:
        pivot = partition(arr, l, r)
        quick_sort(arr, l, pivot - 1)
        quick_sort(arr, pivot + 1, r)
    return arr

