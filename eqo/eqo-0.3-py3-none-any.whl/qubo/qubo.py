import itertools
import numpy as np

from functools import reduce


class KeyFormatError(Exception):
    pass

class QUBO():
    
    def __init__(self, parameters=None):
        self.parameters = {}
        self.n_          = 0
        if parameters:
            for k, v in parameters.items():
                self.__setitem__(k, v)

    def copy(self):
        return (type(self))(self.parameters)

    def absmax(self, ignore_bias=False):
        if ignore_bias:
            return max(abs(v) for k, v in self.parameters.items() if k != ())
        else:
            return max(abs(v) for v in self.parameters.values())

    def scaled(self, scale=1.0):
        return (type(self))({ k: scale * v for k, v in self.parameters.items() })

    def rounded(self):
        return (type(self))({ k: int(v) for k, v in self.parameters.items() })

    def inverse(self):
        return (type(self))({ k: -v for k, v in self.parameters.items() })

    def asMatrix(self, triangle=False):
        m = np.zeros((self.n, self.n))
        for ix, q in self.items():
            if len(ix) == 1:
                (i,) = ix
                m[i, i] = q
            elif len(ix) == 2:
                i, j = ix
                if triangle:
                    m[i, j] = q
                else:
                    m[i, j] = q / 2.0
                    m[j, i] = q / 2.0
        return m

    def asDict(self, forcePairs=False):
        if forcePairs:
            expand = lambda k: (*k, *k) if len(k) == 1 else k
            return { expand(k): v for k, v in self.parameters.items() }
        else:
            return self.parameters.copy()

    def columns(self, n=None):
        if n is None:
            n = self.n_
        for j, i in itertools.product(range(n), repeat=2):
            yield self.__getitem__((i, j))


    def with_tied(self, tied):
        
        first, *rest = tied
        all_tied = set(first).union(*rest)
        
        remaining = list(range(self.n))
        for i in all_tied:
            remaining.remove(i)
            
        mapping = { i: i_ for i_, i in enumerate(remaining) }
        n_remaining = len(remaining)
        
        for i_, group in zip(range(n_remaining, n_remaining+len(tied)), tied):
            mapping.update({ j: i_ for j in group })
            
        Q_ = self.__class__()
        for k, v in self.items():
            if len(k) == 2:
                i, j = k
                Q_[(mapping[i], mapping[j])] += v
            elif len(k) == 1:
                (i,) = k
                Q_[(mapping[i],)] += v
            else:
                Q_[()] += v
                
        #print('mapping:', mapping)
        return Q_
    
    
    def with_inverted(self, inverted):
        if not inverted:
            return self.copy()
        
        Q = self.__class__()
        
        for k, v in self.items():
            if len(k) == 2:
                i, j = k
                if i in inverted:
                    if j in inverted:
                        Q[(i,j)] += v
                        Q[(i,)] -= v
                        Q[(j,)] -= v
                        Q[()] += v
                    else:
                        Q[(i,j)] -= v
                        Q[(j,)] += v
                else:
                    if j in inverted:
                        Q[(i,j)] -= v
                        Q[(i,)] += v
                    else:
                        Q[(i,j)] += v
                        
            elif len(k) == 1:
                if k[0] in inverted:
                    Q[k]  -= v
                    Q[()] += v
                else:
                    Q[k] += v
            else:
                Q[()] += v
                
        return Q
    

    def with_fixed(self, fixed):
        """fixVariables.

        Fix given variables to values in {0, 1} to reduce the QUBO dimension.
        
        Parameters
        ----------
        fixed : dict
            Keys are variable indices, values binary values {0, 1}

        """
        
        if fixed == {}:
            return self.copy()
        
        ones           = sorted([int(i) for i, v in fixed.items() if v == 1])
        remaining_vars = sorted(list(map(int, set(range(self.n)) - set(fixed.keys()))))
        
        R = QUBO()
        
        for i, v in enumerate(remaining_vars):
            R[(i,)] = self[(v,)] + sum(self[(v, w)] for w in ones)
                
            for j, w in enumerate(remaining_vars[:i]):
                R[(i, j)] = self[(v, w)]
        
        R[()] = self[()]
        for i, v in enumerate(ones):
            for _, w in zip(range(i+1), ones):
                R[()] += self[(v, w)]
        
        return R

    def __repr__(self):
        return self.parameters.__repr__()

    def __getitem__(self, k):
        k_ = self.__format_key(k)
        try:
            return self.parameters[k_]
        except KeyError:
            return 0

    def __setitem__(self, k, v):
        k_ = self.__format_key(k)
        if v == 0:
            try:
                del self.parameters[k_]
                if (len(k_) > 0) and (max(k_)+1 == self.n_):
                    # re-calculate n
                    keys = list(map(max, self.keys()))
                    if keys and keys != [()]:
                        self.n_ = max(map(max, self.keys()))+1
                    else:
                        self.n_ = 0
            except KeyError:
                pass
        else:
            if len(k_) > 0:
                self.n_ = max(self.n_, max(k_)+1)
            self.parameters[k_] = v

    def __format_key(self, k):
        if isinstance(k, tuple):
            if len(k) == 2:
                i, j = sorted(k)
                if i == j:
                    return (i,)
                else:
                    return (i, j)
            return k
        else:
            raise KeyFormatError(str(k))

    def keys(self):
        return self.parameters.keys()

    def values(self):
        return self.parameters.values()

    def items(self):
        return self.parameters.items()

    def map(self, f):
        Q = type(self)()
        for k, v in self.items():
            k_, v_ = f(k, v)
            Q[k_] += v_
        return Q

    @property
    def n(self):
        return self.n_

    @property
    def max_index(self):
        return self.n_-1

    def update(self, parameters):
        for k, v in parameters.items():
            self.__setitem__(k, v)

    def subs(self, *args, **kwargs):
        """
        substitute symbols from sympy
        """
        
        d = self.__class__()

        for k, v in self.items():
            try:
                val = float(v.subs(*args, **kwargs))
            except AttributeError:
                val = v
            except TypeError:
                val = v.subs(*args, **kwargs)
            finally:
                d[k] = val

        return d

    def value(self, solution):
        if isinstance(solution, dict):
            value = 0
            for k, v in self.parameters.items():
                if all(solution[i] > 0 for i in k):
                    value += v
            return value
        elif isinstance(solution, np.ndarray):
            return self.value(dict(enumerate(solution)))
        else:
            raise NotImplementedError('solution type not supported!')


class Ising(QUBO):

    def __init__(self, parameters=None):
        super().__init__(parameters)

    def value(self, solution):
        if isinstance(solution, dict):
            value = 0
            for k, v in self.parameters.items():
                sign = reduce(lambda x,y: x*y, [ solution[i] for i in k ], 1)
                value += sign * v
            return value
        else:
            raise NotImplementedError('Ising can only evaluate dicts')

    def with_fixed(self, fixed):
        raise NotImplementedError()
