# linear.py
def linear(lst: list, target: int or str) -> int:
    """ `linear` takes a list of length n and a target value. 
    Each item in the list is compared against the target value until a 
    match is found. `linear_search` returns the INDEX corresponding to 
    the first identified match. If no match found, function returns -1.

    >>> linear([5, 2, 1, 0, 4, 10], 0)
    3

    >>> linear(['a', 'b', 'c'], 'd')
    -1
    """

    index = 0 #set index to zero

    while index < len(lst): #iterate list

        if lst[index] == target: #compare value at current index to target value

            return index #return index if target match

        index+=1 #increment index

    return -1 #return -1 if no match is found by loop completion