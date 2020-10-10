# binary.py
def binary(lst: list, low: int, high: int, target: int or str) -> int:
    """ `binary` takes a SORTED list of length n, a low index, a high index, and a target value, 
        and returns the index of the target value in the list, if present. If no 
        match is identified, `binary_search` returns -1.

        >>> binary([0, 1, 4, 10, 11, 13, 21], 10)
        3

        >>> binary(['a', 'b', 'c'], 'b')
        1

        >>> binary(['a', 'b', 'c'], 'd')
        -1
    """

    if (high >= low): #base case

        mid = (high + low) // 2 #mid is defined as the average of our low and high indices

        if lst[mid] == target: #check if target == mid value
            return mid
        
        elif target > lst[mid]: #check if target > mid value
            return binary(lst, mid+1, high, target)
        
        else: #if target < mid value
            return binary(lst, low, mid-1, target)
    else:
        return -1
        