import numpy as np
from nengo_spa.algebras.hrr_algebra import HrrAlgebra
from nengo.utils.numpy import is_number

class HrrAlgebra(HrrAlgebra):
    def fractional_bind(self, A, b):
        """Fractional circular convolution.""" 
        if not is_number(b):
            raise ValueError("b must be a scalar.")
        return np.fft.ifft(np.fft.fft(A, axis=0)**b, axis=0)
    
    def bind(self, a, b):
        n = len(a)
        if len(b) != n:
            raise ValueError("Inputs must have same length.")
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b), n=n)