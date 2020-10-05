# Personal Base Code

# SVD_interpreter
import numpy as np


def concept_extractor(Vt,fields,n_concepts,n_fields):
    """
    Extarcts concepts from singular value decomposition of a matrix.
    :param Vt: Vt from SVD -- np.linalg.svd(A,full_matrices = False)
    :param fields: labels of columns from labeled dataset (non vectorixed)
    :param n_concepts: number of conecpts to extract. It is best to plot the sigma values and use the elbow curve to extract this number
    :param n_fields: arbitrary number which extracts the top n fields within a topic 
    :return:
    """
    extract_fields = lambda x: [fields[i] for i in np.argsort(x)[:-n_fields:-1]]
    top_concepts = [extract_fields(i) for i in Vt[:n_concepts]]
    return [" ".join(i) for i in top_concepts]


def concept_assigner(U,n_concepts):
    """
    Assigns concepts from singular value decomposition of a matrix.
    :param U:
    :param n_concepts:
    :return:
    """
    return [np.argsort(U[i,:n_concepts])[-1] for i in U]


# Geometrical tools

def distance_to_line(point,coef):
    """
    # https://stackoverflow.com/questions/39840030/distance-between-point-and-a-line-from-two-points
    calculates the distance between a point and a line
    :param point: tuple with (x,y)
    :param coef: tuple with (slope, intercept)
    :return:
    """
    return abs( (coef[0]*point[0]) - point[1]+coef[1] ) / np.sqrt( (coef[0]**2) + 1)


def distance_to_point(p1,p2):
    """
    # https://www.wolframalpha.com/educators/lessonplans/Calculating_Distances_in_Two_and_Three_Dimensions.pdf
    calculated the distance between two points (on a 2D plane)
    :param p1: tuple of a point (x,y)
    :param p2: tuple of a point (x,y)
    :return:
    """
    return np.sqrt( (p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 )

def slope_intercept(p1,p2):
    """
    find slope between two 2D points
    :param p1:
    :param p2:
    :return:
    """
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    intercept = p1[1] - slope*p1[0]
    return (slope,intercept)

def elbow_finder(arr):
    arr = np.sort(arr)[::-1]
    npoints = len(arr)
    coordinates = np.vstack((range(npoints),arr))
    slp_intercept = slope_intercept(coordinates[0],coordinates[-1])
    max_dist = 0
    elbow = 0
    for i in coordinates:
        d = distance_to_line(i, slp_intercept)
        if distance_to_line(i , slp_intercept) >  max_dist:
            max_dist = d
            elbow = i[0]
    return elbow

def binary_search_closest(nums, targ):
    """
    finds the closest left index for a target value. 
    use case: given a set of classes and corresponding cumulative weights (adding up to 1) and a random number (between 0 and 1), find which class does the random number belong to. -- Jason@Insight 02.2020
    
    nums: list; Int or Float numbers 
    targ: int or Float; target value
    
    output: int; the index of the closest left index for the targ in nums
    """
    if len(nums) < 1: raise ValueError(f"input array nums, {nums} is empty")
    if targ > nums[-1]: return -1
    low = 0
    high = len(nums) - 2
    while low <= high:
        mid = (low+high)//2
        if nums[mid] < targ < nums[mid+1]:
            return mid
        elif targ > nums[mid]:
            low = mid + 1
        elif targ < nums[mid]:
            high = mid - 1
    return 0 # if no satisfactory range is found
    
def tree_view(d, print_keys=[], level=0):
    """
    json viewer
    d : json path
    print_keys : keys for which dats will be printed
    level : leave at 0 to print a growing tree
    """
    if "keys" not in dir(d):
        return
    for k in d.keys():
        d2 = d[k]
        print("--"*level, k)
        if type(d2) == list and len(d2) > 0:
            tree_view(d2[0], level+1,print_keys=print_keys)
        if k in print_keys:
            print(d2)
        tree_view(d2, level+1,print_keys=print_keys)

def splitter(string,max_len=300,final=[]):
    """
    splits a longer string into multiple smaller strings
    :param string: string which requires splitting
    :param final: intially empty final list of reduced strings
    :return: final list
    
    # BUG: function has to be run with final=[] when called. Otherwise, duplicate entried will be populated.
    """

    split_string = string.split()
    split_len = len(split_string)
    if split_len < max_len:
        final.append(string)
    else:
        split_idx = min(round(len(split_string)/2),max_len)
        join1,join2 = " ".join(split_string[:split_idx])," ".join(split_string[split_idx:])
        final.append(join1)
        splitter(join2, max_len, final)
    return final







