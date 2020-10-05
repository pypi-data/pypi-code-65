import itertools
import numpy as np
from tqdm import tqdm

def bruteForceAggregate(Q, fCombine, fId=lambda x: x, quiet=False): #, init=[]):
    """
    Aggretate all loss values run through `fId` using a function `fCombine`.
    The function `fCombine` should be associative.
    """
    n = Q.max_index+1
    z = 0.0
    for x in tqdm(itertools.product([0, 1], repeat=n), total=2**n, disable=quiet):
        loss = Q.value(dict(enumerate(x)))
        z = fCombine(z, fId(loss))
    return z
    
    #if len(init) == Q.max_index+1:
        #loss = evaluate(Q, { i: b for i, b in enumerate(init) })
        #return fId(loss)
    #z1 = bruteForceAggregate(Q, fCombine, fId, init=init+[0])
    #z2 = bruteForceAggregate(Q, fCombine, fId, init=init+[1])
    #return fCombine(z1, z2)
    
def bruteForceMinimum(Q, quiet=False):
    return bruteForceAggregate(Q, min, quiet=quiet)

def bruteForceMaximum(Q, quiet=False):
    return bruteForceAggregate(Q, max, quiet=quiet)

def bruteForceMAP(Q):
    n = Q.n
    loss_map = float('-inf')
    for x in itertools.product([0,1], repeat=n):
        loss = Q.value(dict(enumerate(x)))
        if loss > loss_map:
            x_map    = x
            loss_map = loss
    
    return dict(enumerate(x_map)), loss_map
    
def bruteForceLogPartition(Q, quiet=False):
    return np.log(bruteForceAggregate(Q, fCombine=lambda x, y: x+y, fId=np.exp, quiet=quiet))

def parameterBounds(Q, ignoreBias=False):
    """parameterBounds.
    
    Returns the smallest and largest parameter present in ``Q``.
    
    Return
    ------
    res : tuple containing minimum and maximum parameter value
    
    """
    if Q.n == 0:
        return (0, 0)
    
    if ignoreBias:
        bias = Q[()]
        Q[()] = 0

    it = iter(Q.values())
    minp = maxp = next(it)
    for v in it:
        if v < minp:
            minp = v
        elif v > maxp:
            maxp = v
    
    if ignoreBias:
        Q[()] = bias

    return (minp, maxp)

def minimalScaleFactor(Q):
    values = { Q[k] for k in set(Q.keys()) - {()} }
    mindiff = None
    for p, q in itertools.combinations(values, r=2):
        diff = np.abs(p-q)
        try:
            if diff < mindiff:
                mindiff = diff
        except TypeError: # mindiff is still None
            mindiff = diff
            
    return 1.0 / mindiff

def minimalBitLength(Q):
    s = minimalScaleFactor(Q)
    return int(np.ceil(np.log2(s+1)+1))

def checkRoundingErrors(Q, bits=16):
    minp, maxp = parameterBounds(Q)
    maxabsp = max(np.abs(minp), np.abs(maxp))
    invalpha = maxabsp / (2**(bits-1)-1)
    mindiff = 1.0 / minimalScaleFactor(Q)
    return mindiff < invalpha
        
def impact(Q, i):
    n = Q.max_index+1
    
    neighborhood = { j for j in range(n) if Q[(i,j)] != 0 }
    neighborhood.add(i)
    
    Q_ = fixVariables(Q, { i: 0 for i in set(range(n)) - neighborhood })
    i_ = sorted(neighborhood).index(i)
    js = set(range(len(neighborhood))) - {i_}
    
    minImpact=2**32-1
    maxImpact=-2**32
    
    for bs in itertools.product([0, 1], repeat=len(neighborhood)):
        x = dict(zip(js, bs))
        
        x[i_] = 0
        L0 = evaluate(Q_, x)
        
        x[i_] = 1
        L1 = evaluate(Q_, x)
        
        impact = L1 - L0
        if impact < minImpact:
            minImpact = impact
        elif impact > maxImpact:
            maxImpact = impact
    
    return minImpact, maxImpact

def sampled_logz(Q, iterations=None):
    if iterations is None:
        iterations = 2**(Q.n//2) if Q.n <= 40 else 2**20

    Z = 0 
    for i in range(iterations):
        x  = np.random.binomial(1, 0.5, size=Q.n)
        Z += np.exp(Q.value(x))

    return np.log(Z) - np.log(iterations)


def naive_1opt(Q, x):
    M = Q.asMatrix(triangle=False)
    lin = np.diagonal(M).copy()   # extract linear terms
    np.fill_diagonal(M, 0) # remove diagonal elements
    x_ = np.fromiter(x.values(), dtype=np.int64) if type(x) is dict else x

    def gains(x__):
        delta_x = 1-2*x__
        gs_  = lin*delta_x
        gs_ += 2*delta_x*np.dot(x__, M)
        return gs_

    gs = gains(x_)
    gs_ixs = np.where(gs > 0)[0]

    while gs_ixs.size > 0:
        k = np.random.choice(gs_ixs)
        x_[k] = 1 - x_[k]
        gs = gains(x_)
        gs_ixs = np.where(gs > 0)[0]

    return x_

def randkopt(Q, x=None):
    if x is None:
        x = np.random.binomial(1, 0.5, Q.n)
    else:
        if type(x) is dict:
            x_ = np.zeros(Q.n, dtype=np.int64)
            for i, v in x.items():
                x_[i] = v
            x = x_

    M = Q.asMatrix(triangle=False)
    lin = np.diagonal(M).copy()   # extract linear terms
    np.fill_diagonal(M, 0) # remove diagonal elements

    def gains(x_):
        delta_x = 1-2*x_
        gs_  = lin*delta_x
        gs_ += 2*delta_x*np.dot(x_, M)
        return gs_

    # def update_gains(gs_, k_, x_):
    #     delta_x = 1-2*x_
    #     delta_gs = (4*x_[k_]-2)*np.dot(delta_x, M)
    #     gs_ += delta_gs
    #     gs_[k_] -= delta_gs[k_]
    #     gs_[k_] *= -1

    gs = gains(x)

    while True:
        x_prev = x.copy()
        G_max  = 0
        G      = 0
        C      = set(range(Q.n))
        while True:

            RP = np.random.choice(Q.n, Q.n, replace=False)
            for k in RP:
                if gs[k] > 0:
                    G += gs[k]
                    G_max = G
                    x[k] = 1 - x[k]   # invert at index k
                    x_best = x.copy()
                    gs = gains(x)     # update gains
                    if k in C:
                        C.remove(k)

            j = max(C, key=lambda h: gs[h])
            G += gs[j]
            if G > G_max:
                G_max  = G
                x_best = x.copy()
            x[j] = 1 - x[j]       # invert at index j
            C.remove(j)
            gs = gains(x)         # update gains

            if len(C) == 0:
                break

        if G_max > 0:
            x = x_best.copy()
        else:
            x = x_prev.copy()

        if G_max <= 0:
            return x, Q.value(dict(enumerate(x)))




