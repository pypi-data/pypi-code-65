import numpy as np
from nengo.dists import Distribution, UniformHypersphere
from nengo_ssp.hrr_algebra import HrrAlgebra
from nengo_ssp.utils import ssp_vectorized


class UniformSSPs(Distribution):
# Get SSPs representing positions uniformly distributed. For setting encoders   

    def __init__(self, basis, alg = HrrAlgebra(), radius = 1):
        super().__init__()
        self.radius = radius
        self.basis = np.vstack([X.v for X in basis]).T
        #np.vstack([X.v, Y.v]).T
        self.alg = alg
        self.N = len(basis)
 
    def sample(self, n, d=None, rng=np.random):
            
        unif_dist = UniformHypersphere()
        xy = unif_dist.sample(n, self.N)*self.radius
        
        return ssp_vectorized(self.basis, xy).real

    
