class Search:
    """Defines the following set of search algorithms as `@classmethods`: 
    `Search.linear(lst, target)`, `Search.binary(lst, target)` 
    """

    @classmethod
    def linear(cls, lst: list, target: int or str) -> int:
        """ `linear_search` takes a list of length n and a target value. 
        Each item in the list is compared against the target value until a 
        match is found. `linear_search` returns the INDEX corresponding to 
        the first identified match. If no match found, function returns -1.

        >>> Search.linear([5, 2, 1, 0, 4, 10], 0)
        3

        >>> Search.linear(['a', 'b', 'c'], 'd')
        -1
        """

        index = 0 #set index to zero

        while index < len(lst): #iterate list

            if lst[index] == target: #compare value at current index to target value

                return index #return index if target match

            index+=1 #increment index

        return -1 #return -1 if no match is found by loop completion

    @classmethod
    def binary(cls, lst: list, low: int, high: int, target: int or str) -> int:
        """ `binary_search` takes a SORTED list of length n, a low index, a high index, and a target value, 
            and returns the index of the target value in the list, if present. If no 
            match is identified, `binary_search` returns -1.

            >>> binary_search([0, 1, 4, 10, 11, 13, 21], 10)
            3

            >>> binary_search(['a', 'b', 'c'], 'b')
            1

            >>> binary_search(['a', 'b', 'c'], 'd')
            -1
        """

        if (high >= low): #base case

            mid = (high + low) // 2 #mid is defined as the average of our low and high indices

            if lst[mid] == target: #check if target == mid value
                return mid
            
            elif target > lst[mid]: #check if target > mid value
                return cls.binary(lst, mid+1, high, target)
            
            else: #if target < mid value
                return cls.binary(lst, low, mid-1, target)
        else:
            return -1
            
        

