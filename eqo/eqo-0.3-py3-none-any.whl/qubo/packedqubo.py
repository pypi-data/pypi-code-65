import bitarray  as B
from .qubo import *


class VariableLimitExceededException(Exception):
    pass


class PackedQUBO():

    def __init__(self, max_variables=2048):
        self.max_variables = max_variables
        
        self.__qubo    = QUBO()
        self.__offsets = []
        self.__biases  = []
        self.__scales  = []

    @property
    def num_qubos(self):
        return len(self.__offsets)
    
    @property
    def max_index(self):
        return self.__qubo.n - 1
    
    def append(self, Q, scale=1.0):
        n = Q.n
        
        if self.__qubo.n+n >= self.max_variables:
            raise VariableLimitExceededException('Cannot exceed limit of {self.max_variables} variables!')
        
        offset = self.__offsets[-1] if len(self.__offsets) > 0 else 0
        
        self.__qubo.update({ tuple(map(lambda i: i+offset, k)): v for k, v in Q.items() if len(k) > 0 })
        self.__qubo[()] += Q[()]
        self.__biases.append(Q[()])
        self.__offsets.append(offset+n)
        self.__scales.append(scale)

    def clear(self):
        self.__qubo    = QUBO()
        self.__offsets.clear()
        self.__biases.clear()
        self.__scales.clear()

    def packed(self):
        return self.__qubo.copy()

    def unpacked(self):
        Qs = [ QUBO({ (): bias }) for bias in self.__biases ]
        for k, v in self.__qubo.items():
            try:
                i = k[0] # just need any index
                # determine which QUBO instance this key belongs to 
                qubo_ix = next(ix for ix, o in enumerate(self.__offsets) if i < o) # "find first.."
                offset = self.__offsets[qubo_ix-1] if qubo_ix > 0 else 0
                Qs[qubo_ix][tuple(map(lambda i: i-offset, k))] = v
            except IndexError:
                # k is ()
                pass
            
        return Qs
            
    def evaluate_all(self, inp):
        if isinstance(inp, bytes):
            # assume this is big-endian, as is the FPGA output
            ba = B.bitarray(format(int.from_bytes(inp, byteorder='big', signed=False), f'0{self.__qubo.max_index+1}b'))
            ba.reverse()
            x  = { i: int(ba[i]) for i in range(self.max_index+1) }
        elif isinstance(inp, dict):
            x = inp
        else:
            raise NotImplementedError('PackedQUBO can only take bytestrings or dicts for evaluation')
        
        Qs = self.unpacked()
        values = []
        for qubo_ix in range(len(self.__offsets)):
            o_from = self.__offsets[qubo_ix-1] if qubo_ix > 0 else 0
            o_to   = self.__offsets[qubo_ix]
            scale  = self.__scales[qubo_ix]
            
            x_ = { i-o_from: b for i, b in x.items() if o_from <= i < o_to }
            values.append(Qs[qubo_ix].value(x_)/scale)
            
        return values
