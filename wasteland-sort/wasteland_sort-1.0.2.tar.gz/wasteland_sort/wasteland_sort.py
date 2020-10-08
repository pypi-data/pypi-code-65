from typing import Union

def wasteland_sort(landmarks: list, reverse: bool) -> list:
    """ O(m+n) integer sorting algorithm developed with the intent of providing better performance than widely-used sorts 
    in terms of both memory and time for integer sorting. Currently runs in O(m_n) time and O(max(m, n)) space.
    
    Parameters
    ----------
    landmarks: List[int]
        List of integers to be sorted
    
    reverse: bool
        True if you want to sort integers in reverses

    
    Returns
    -------
    Pseudo in-place landmarks array. Each value is actually replaced with another integer.
    """
    if len(landmarks) < 1:
        return landmarks
    least, most = find_extremes(landmarks)

    wasteland: list = [0] * (most - least + 1)
    index : int = 0
    for value in landmarks:
        index = value - least
        wasteland[index] += 1

    index = 0


    for x in range(len(wasteland)):
        item: int = wasteland[x]
        while item > 0:
            item -= 1
            if reverse:   
                landmarks[(len(landmarks) - 1) - index] = least + x
            else:
                landmarks[index] = least + x   
            index += 1
        
    



#######Helper Functions#######
def find_extremes(landmarks: list) -> Union[int, int]:
    """ Helper function to find the maximum and minimum elements in a list in O(n) time

    Parameters
    ----------
    landmarks: List[int]
        List of integers to be searched
    

    Returns
    -------
    Two integers: the minimum value and the maximum value in that order
    """
    if landmarks == []:
        raise ValueError("Could not find maxima of the list")

    most, least = landmarks[0], landmarks[0]

    for val in landmarks:
        if val > most:
            most = val
        if val < least:
            least = val
    return least, most
