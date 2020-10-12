import numpy as np


def to_binary(n, dim):
        """
        Obtains the binary representation of an integer.
        args:
            n: The integer to be converted to binary. The integer shouldn't
            be so large that more than dim(the next arg) bits are required
            to encode it.
            dim: The dimension of the array that is
                going to contain the binary representation.
        """
        raw = np.zeros(dim)
        temp = n%(2**dim)
        indx = 0
        while temp > 0:
            raw[indx] = temp % 2
            temp = int(temp / 2)
            indx = indx + 1
        return raw


class GenBase():
    """
    Represents an integer in a base system where the bases are not constant, but given by an array.
    For example, a binary base system has bases equal to 2 while decimal has all bases equal to 10.
    But what if the "units" digit had a base 3 (could take values 0,1,2) and the "tens" digit had a 
    base 4 (could take values 0,1,2,3) and so on.
    """
    def __init__(self, base_vals):
        """
        Instantiates an instance of ArrayRep class.
        args:
            base_vals: The values of the bases given by an array.
        """
        self.bases = base_vals
        self.arr_vals = np.zeros(len(base_vals))
    
    def add_one(self):
        """
        Whatever the integer value of the instance of this class currently is, add one to it.
        TODO: If an integer is greater than the maximum allowable per the array, modulo it
              with max permissible value.
        """
        self.arr_vals[0] += 1
        i = 0
        while self.arr_vals[i] > self.bases[i]:
            self.arr_vals[i] = 0
            self.arr_vals[i+1] += 1
            i+=1
    
    def add_num(self,no):
        """
        Whatever the integer value of the instance of this class currently is, 
        add an integer, no to it.
        args:
            no: The number to add.
        """
        for _ in range(no):
            self.add_one()

