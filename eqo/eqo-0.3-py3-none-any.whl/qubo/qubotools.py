import bitarray as BA
import itertools
import numpy    as np
import struct

from .qubo          import *
from .analyze       import parameterBounds
from collections    import defaultdict
from random         import choices
from tqdm           import tqdm


####################################
# Methods to create QUBO Instances #
####################################

def one_max(dimension):
    return QUBO({ (i,): -1 for i in range(dimension) })

def random(dimension, low=-1.0, high=1.0, external=False, extLow=-1.0, extHigh=1.0, density=1.0, seed=None, ising=False):
    if seed is not None:
        np.random.seed(seed)
    
    Q = Ising() if ising else QUBO()
    Q.update({ (i, j): np.random.uniform(low=low, high=high) for i, j in itertools.combinations(range(dimension), r=2) if np.random.uniform() <= density })
    if external:
        for i in range(dimension):
            if np.random.uniform() <= density:
                Q[(i,)] = np.random.uniform(low=extLow, high=extHigh)
    return Q

def random_grid(xy, low=-1.0, high=1.0, external=False, extLow=-1.0, extHigh=1.0, density=1.0, seed=None, ising=False):
    # internal function for neighbors within a grid
    def neighbors(size_x, size_y):
        n = size_x * size_y
        for i in range(n):
            above = i - size_x
            left  = i - 1
            if above >= 0:
                yield (i, above)
            if i % size_x > 0:
                yield (i, left)
    
    if seed is not None:
        np.random.seed(seed)
    
    (x, y) = xy
    Q = Ising() if ising else QUBO()
    Q.update({ (i, j): np.random.uniform(low=low, high=high) for i, j in neighbors(x, y) if np.random.uniform() <= density })
    if external:
        for i in range(x*y):
            if np.random.uniform() <= density:
                Q[(i,)] = np.random.uniform(low=extLow, high=extHigh) 
    return Q

def random_chain(length, sampleWeight, sampleExt, ising=False):
    
    if ising:
        Q = Ising()
    else:
        Q = QUBO()
        
    for i in range(length-2):
        Q[(i, i+1)] = sampleWeight()
        Q[(i,)]     = sampleExt()
    Q[(length-1,)] = sampleExt()
      
    return Q
    
def fromMatrix(m, linear=None, ising=False):
    """
    Create QUBO from upper triangle matrix. If `ising` is set to True,
    The given parameters are interpreted as Ising parameters, and the
    Ising model is automatically converted to a QUBO instance.
    """
    Q = Ising() if ising else QUBO()
    for i, j in itertools.combinations_with_replacement(range(m.shape[0]), r=2):
        Q[(i, j)] = m[i, j]
    if linear is not None:
        for i, p in enumerate(linear):
            Q[(i,)] += p
    return ising_to_qubo(Q) if ising else Q

def fromMarkovModel(model, digits=8, return_clique_ranges=False):
    """
    Create QUBO from instance of pgmpy's MarkovModel class
    """
    
    Q = QUBO()
    
    # build map: QUBO Index -> Variable Values
    qubo_to_var = {}
    # build another map: Clique Index -> (QUBO Index from, QUBO Index to)
    factor_to_qubo = {}

    i = 0
    for fi, f in enumerate(model.factors):
        factor_start = i
        for vi, v in np.ndenumerate(f.values):
            v_ = round(v, digits)
            if v_ != 0:
                Q[(i,)] = - v_ # negate to make this a minimization problem!
                qubo_to_var[i] = vi
                i += 1
        factor_stop = i
        factor_to_qubo[fi] = (factor_start, factor_stop)

    penalty = sum(abs(v) for v in Q.values())

    # add penalty weights to conflicting variable pairs
    for ix_from, ix_to in factor_to_qubo.values():
        for i, j in itertools.combinations(range(ix_from, ix_to), r=2):
            Q[(i, j)] = penalty

    for (fi1, f1), (fi2, f2) in itertools.combinations(enumerate(model.factors), r=2):
        common_variables = set(f1.variables).intersection(f2.variables)
        if common_variables:
            variable_indices = [ (f1.variables.index(v), f2.variables.index(v)) for v in common_variables ]
            r1 = range(*factor_to_qubo[fi1])
            r2 = range(*factor_to_qubo[fi2])
            for i, j in itertools.product(r1, r2):
                if any([ qubo_to_var[i][vx1] != qubo_to_var[j][vx2] for vx1, vx2 in variable_indices ]):
                    # variables have different assignments
                    Q[(i, j)] = penalty

    if return_clique_ranges:
        return Q, list(factor_to_qubo.values())
    else:
        return Q

def encodeMarkovState(state, model, digits=8):
    one_indices = []
    i = 0
    for f in model.factors:
        variables = f.variables
        # look up states of all variables involved
        actual_state = tuple(map(lambda vr: state[vr], variables))
        # iterate over all possible clique states and check, which corresponds to the actual state
        for variable_state, v in np.ndenumerate(f.values):
            v_ = round(v, digits)
            if v_ != 0:
                if variable_state == actual_state:
                    one_indices.append(i)
                    # CAVEAT: If the actual state was previously unobserved, i.e. v (aka θ) == 0,
                    # then the state indicator vector will be all 0, which is invalid.
                i += 1

    arr = np.zeros(i, dtype=np.int64)
    for j in one_indices:
        arr[j] = 1
    return arr

def decodeMarkovState(x, model, digits=8):
    for f in model.factors:
        for variable_state, v in np.ndenumerate(f.values):
            pass
    
    raise NotImplementedError()

def fromUAI(filename, **kwargs):
    from pgmpy.models    import MarkovModel
    from pgmpy.readwrite import UAI
    reader = UAI.UAIReader(filename)
    model = reader.get_model()
    if isinstance(model, MarkovModel):
        return fromMarkovModel(model, **kwargs)
    else:
        raise RuntimeError('File contains no Markov model')


def randomEC3(n, m=None, alpha=None):
    if m is None:
        m = round(alpha * n)
    
    Q = QUBO()

    # constant term
    Q[()] = m

    for i in range(m):
        # sample random clause
        u, v, w = np.random.choice(n, 3, replace=False)
        
        # linear terms
        Q[(u,)] -= 1
        Q[(v,)] -= 1
        Q[(w,)] -= 1

        # quadratic terms
        Q[(u,v)] += 2
        Q[(u,w)] += 2
        Q[(v,w)] += 2
        
    return Q

def toEC3(x, m=None, alpha=None):
    n = len(x)
    if m is None:
        m = round(alpha * n)
    x_ = np.fromiter(x.values(), dtype=np.int64) if type(x) is dict else x

    zeros = np.where(x_ == 0)[0]
    ones  = np.where(x_ == 1)[0]

    Q = QUBO()

    # constant term
    Q[()] = m

    for i in range(m):
        # sample clause
        u    = np.random.choice(ones)
        v, w = np.random.choice(zeros, 2)

        # linear terms
        Q[(u,)] -= 1
        Q[(v,)] -= 1
        Q[(w,)] -= 1

        # quadratic terms
        Q[(u,v)] += 2
        Q[(u,w)] += 2
        Q[(v,w)] += 2
    
    return Q
    

#############################
# Methods for QUBO file I/O #
#############################

def _tuple2index(t, n):
    l = len(t)
    if l == 0:
        return 0
    else:
        try:
            i, j = t
        except ValueError:
            (i,) = t
            j = i

        return (i*(2*n-i-1)//2)+j+1

# [(), (0,), (0,1), (0,2) ... (0,n-1), (1,), (1,2), (1,3) ... (1,n-1), (2,), (2,3) ... ]
def _index2tuple(ix, n):
    if ix == 0:
        return ()
    else:
        inv_ix = n*(n+1)//2 - ix
        inv_i = int(np.sqrt(2*inv_ix+0.25)-0.5)
        inv_j = inv_ix - inv_i*(inv_i+1)//2
        if inv_i == inv_j:
            return (n-inv_i-1,)
        else:
            return (int(n-inv_i-1), int(n-inv_j-1))
         

def toFile(Q, filename, scale=False, paramBytes=4):
    """toFile.

    Write QUBO (or PUBOMatrix) instance to file.

    Parameters
    ----------
    Q : QUBO instance.
    filename : str.

    Notes
    -----
    The variable names (i.e. the mapping) should be verbatim, so ``Q.mapping`` should be ``{0: 0, 1: 1, ...}``.

    """
    n = Q.n
    if n > 65535:
        raise Exception('Can only save QUBOs with max. 65536 variables')
    if scale and (paramBytes <= 0 or paramBytes > 65535):
        raise Exception('paramBytes must be in [1 .. 65535] when using scale option')

    uint16 = lambda x: int.to_bytes(x, length=2, byteorder='big', signed=False)
    double = lambda x: struct.pack('>d', x)

    # calculate scaling factor
    (low, high) = parameterBounds(Q)
    factor = (2.0**(8*paramBytes-1)-1) / max(np.abs(low), np.abs(high)) if scale else 1.0
    
    scaledInt = lambda x: int.to_bytes(int(x*factor), length=paramBytes, byteorder='big', signed=True)
    
    encode_w    = double if not scale else scaledInt
    bytes_per_w = 8      if not scale else paramBytes

    with open(filename, 'wb') as f:
        # write max index (n-1)
        f.write(uint16(n-1))

        # write number of bits when scaling, 0 otherwise
        if scale:
            f.write(uint16(paramBytes))
            f.write(double(factor))
        else:
            f.write(uint16(0))

        # do partial run-length encoding only for consecutive zeros
        lastIx = -1
        for e, v in sorted(Q.items()):
            ix = _tuple2index(e, n)
            gap = ix - lastIx - 1
            if gap > 0:
                f.write(encode_w(0))
                while gap >= 65535:
                    f.write(uint16(65535))
                    gap -= 65535
                f.write(uint16(gap))
                
            f.write(encode_w(v))
            lastIx = ix
            
def fromFile(filename, rescale=True, ising=False):
    """fromFile.
    
    Load QUBO (or PUBOMatrix) instance from file, using the given keys verbatim as binary variable names.

    Parameters
    ----------
    filename : str.

    Return
    ------
    Q : QUBO instance.

    """
    uint       = lambda x: int.from_bytes(x, byteorder='big', signed=False)
    signed_int = lambda x: int.from_bytes(x, byteorder='big', signed=True)
    double     = lambda x: struct.unpack('>d', x)[0]
    
    Q = Ising() if ising else QUBO()

    with open(filename, 'rb') as f:
        # read number of variables (n)
        n = uint(f.read(2))+1
        paramBytes = uint(f.read(2))

        if paramBytes == 0:
            factor = 1.0
            decode_w = double
            bytes_per_w = 8
        else:
            factor = double(f.read(8))
            decode_w = signed_int
            bytes_per_w = paramBytes
        
        ix = 0
        max_ix = n*(n+1)//2
        data = f.read(bytes_per_w)
        while data != b'':
            w = decode_w(data)
            if w == 0.0:
                gap = uint(f.read(2))
                while gap == 65535:
                    ix += gap
                    gap = uint(f.read(2))
                ix += gap
            else:
                Q[_index2tuple(ix, n)] = w/factor if rescale else w
                ix += 1
            data = f.read(bytes_per_w)

    return ising_to_qubo(Q) if ising else Q

def toDWaveFile(Q, filename, comment=None):

    M = Q.asMatrix(triangle=True)

    nNodes = M.shape[0]
    nCouplers = np.sum(np.triu(M, 1) != 0)
    maxNodes = int(2 ** np.ceil(np.log2(Q.n))) # nearest power of 2

    if not filename.lower().endswith('.qubo'):
        filename += '.qubo'

    with open(filename, 'w') as f:

        if comment is not None:
            f.write(f'c {comment}\n')

        f.write(f'p qubo 0 {maxNodes} {nNodes} {nCouplers}\n')
        
        # linear parameters
        f.write('c LINEAR PARAMETERS - - - - - - - -\n')
        for i, p in enumerate(np.diag(M)):
            f.write(f'{i} {i} {p}\n')
        
        # quadratic parameters
        f.write('c QUADRATIC PARAMETERS  - - - - - -\n')
        couplers = 0
        for (i, j), p in np.ndenumerate(M):
            if (p == 0.0) or (i == j):
                continue
            f.write(f'{i} {j} {p}\n')
            couplers += 1

        assert couplers == nCouplers


def fromDWaveFile(filename):
    Q = QUBO()
    with open(filename, 'r') as f:
        for line in map(lambda l: l.strip().lower(), f):
            if line.startswith('c') or line.startswith('p'):
                # line starting with p is not needed
                continue

            i, j, p = line.split()
            Q[(int(i), int(j))] = float(p)
    
    return Q


def columns(Q, dim=None):
    """columns.

    Yield the entire parameter matrix column-wise.

    """
    if dim is None:
        dim = Q.max_index+1
    
    for j in range(dim):
        for i in range(dim):
            yield Q[(i, j)]

def toMatrix(Q, symmetric=False):
    m = np.zeros((Q.max_index+1,)*2)
    for k, v in Q.items():
        try:
            i, j = k
            if symmetric:
                m[i][j] = 0.5 * v
                m[j][i] = 0.5 * v
            else:
                m[i][j] = v
            
        except ValueError:
            try:
                (i,) = k
                m[i][i] = v
                
            except ValueError:
                # ignore global offset
                continue
            
    return m


def interpolate(Q1, Q2, p):
    if Q1.n != Q2.n:
        raise ValueError("QUBO instances must be of equal size to be interpolated")

    Q = QUBO()
    
    for i, j in itertools.combinations_with_replacement(range(Q1.n), r=2):
        v1 = Q1[(i, j)]
        v2 = Q2[(i, j)]
        
        v = v1+p*(v2-v1)
        Q[(i, j)] = v

    return Q


#############################
# Methods to evaluate QUBOs #
#############################

def evaluate(Q, vector):
    f = (lambda x: 2*x-1) if isinstance(Q, Ising) else lambda x: x
    if isinstance(vector, bytes):
        # assume this is big-endian, as is the FPGA output
        ba = BA.bitarray(format(int.from_bytes(vector, byteorder='big', signed=False), f'0{Q.max_index+1}b'))
        ba.reverse()
        x  = { i: int(ba[i]) for i in range(Q.max_index+1)}
    elif isinstance(vector, str):
        # interpret as binary string
        x = { i: f(int(vector[i])) for i in range(len(vector))}
    elif isinstance(vector, set):
        # interpret as set of all indices = 1
        x = { i: f(1 if i in vector else 0) for i in range(Q.max_index+1) }
    elif isinstance(vector, dict):
        x = vector
    else:
        raise Exception(f"Unknown type of QUBO solution: {type(vector)}")
    
    return Q.value(x)
    
def evaluateStacked(S, vector):
    ba = BA.bitarray(format(int.from_bytes(vector, byteorder='big', signed=False), f'0{S.n}b'))
    ba.reverse()
    x  = { i: int(ba[i]) for i in range(S.num_binary_variables)}
    return S.values(x)

def random_solution(n):
    return dict(enumerate(choices([0, 1], k=n)))

def random_mrf_assignment(Q, clique_ranges):
    s = np.zeros(Q.n)
    for i, j in clique_ranges:
        s[np.random.randint(i, j)] = 1

    # perform rejection sampling
    m = toMatrix(Q)
    while np.dot(s, np.dot(m, s)) > 0:
        s = np.zeros(Q.n)
        for i, j in clique_ranges:
            s[np.random.randint(i, j)] = 1

    return { i: int(v) for i, v in enumerate(s) }

###########################
# Methods to modify QUBOs #
###########################

def ising_to_qubo(I):
    Q = QUBO()
    bias = 0.0
    for k, v in I.items():
        if len(k) == 1:
            Q[k] += 2. * v
            bias -= v
        elif len(k) == 2:
            i, j = k
            Q[k] = 4. * v
            Q[(i,)] -= 2. * v
            Q[(j,)] -= 2. * v
            bias += v
    
    Q[()] = I[()] + bias
    return Q

def qubo_to_ising(Q):
    I = Ising()
    lin_bias = 0.0
    qdr_bias = 0.0
    for k, v in Q.items():
        if len(k) == 1:
            I[k] += 0.5 * v
            lin_bias += v
        elif len(k) == 2:
            i, j = k
            I[(i, j)] += 0.25 * v
            I[(i,)] += 0.25 * v
            I[(j,)] += 0.25 * v
            qdr_bias += v
    
    I[()] += Q[()] + 0.5 * lin_bias + 0.25 * qdr_bias
    return I

def add_normal_noise(Q, scale):
    for k in Q.keys():
        Q[k] += np.random.normal(loc=0.0, scale=scale)
