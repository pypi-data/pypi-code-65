import numpy as np


#################
## Failed attempt.
def comb(n,k,arr=[]):
    if len(arr)==k:
        print(arr)
    if len(arr)==0:
        max_itm=-1
    else:
        max_itm = arr[len(arr)-1]
    for j in range(max_itm+1,n):
        arr.append(j)
        comb(n,k,arr)
    arr=[]

comb(4,2)


#############
## Geeksforgeeks solution.

def printCombination(arr, n, r):
    """
    # The main function that prints
    # all combinations of size r in
    # arr[] of size n. This function
    # mainly uses combinationUtil()
    """
    # A temporary array to
    # store all combination
    # one by one
    data = [0]*r
    # Print all combination
    # using temprary array 'data[]' 
    combinationUtil(arr, data, 0,
                    n - 1, 0, r)

def combinationUtil(arr, data, start,
                    end, index, r):
    """
    arr[]: Input Array
    data[]: Temporary array to
             store current combination
    start & end: Staring and Ending
                 indexes in arr[] 
    index: Current index in data[] 
    r: Size of a combination to be printed
    Notes:
    1) end never gets udpated.
    """                         
    if (index == r): 
        print(data)
        return
    #When index is 0, we loop from 0 to ((5-1)-(3-1))=2
    for i in range(start,end-(r-1)+index+1):
        data[index] = arr[i]
        combinationUtil(arr, data, start=i+1,  
                        end=end, index=index+1, r=r)
        ## TODO: adding i+=1 here doesn't break this code. Why??


# Driver Code
def main_driver():
    arr = np.arange(6)
    r = 2
    n = len(arr)
    printCombination(arr, n, r)

